"""Aceitação do nível 5 — registry de modelos + hot-swap em runtime.

Usa um loader FakeYOLO (sem torch). O critério é um invariante determinístico:
depois de cada troca, a versão servida é igual à última definida, e o carregamento
fica em cache por versão. Um smoke test de concorrência verifica que não há estado
corrompido sob threads (uma corrida que passa não *prova* por si só thread-safety
— o GIL pode esconder um swap sem lock — então escreva o swap para ser correto sob
concorrência: carregue o novo modelo por completo, depois publique-o atomicamente
sob um lock).
"""

from __future__ import annotations

import itertools
import threading

import pytest

import ml.registry as registry_mod
from ml.registry import ModelRegistry

VERSIONS = ["1.0.0", "1.1.0", "2.0.0"]


@pytest.fixture
def registry(tmp_path, monkeypatch):
    models = tmp_path / "models"
    models.mkdir()
    for v in VERSIONS:
        (models / f"shapes-detector-v{v}.pt").write_bytes(b"FAKE")

    calls = {"n": 0}

    def fake_load(weights):
        calls["n"] += 1
        return {"weights": str(weights)}  # substituto opaco de um modelo

    monkeypatch.setattr(registry_mod, "load_yolo", fake_load)
    reg = ModelRegistry(models_dir=models)
    reg._loader_calls = calls  # exposto para o assert de load-once
    return reg


def test_discovers_all_versions(registry):
    listing = registry.list_models()
    found = {m.version for m in listing.models}
    assert found == set(VERSIONS)
    assert registry.get_active() is None


def test_switch_sets_active_and_served_model(registry):
    for v in ["1.1.0", "2.0.0", "1.0.0", "2.0.0"]:
        registry.set_active(v)
        assert registry.get_active() == v
        assert registry.active_model_id() == f"shapes-detector-v{v}"


def test_loads_once_per_version(registry):
    registry.set_active("1.0.0")
    registry.set_active("1.0.0")  # em cache: sem recarregar
    registry.set_active("2.0.0")
    registry.set_active("1.0.0")  # ainda em cache
    assert registry._loader_calls["n"] == 2, "cada versão deve carregar no máximo uma vez"


def test_unknown_version_raises(registry):
    with pytest.raises((ValueError, KeyError)):
        registry.set_active("9.9.9")


def test_concurrent_switch_has_no_torn_state(registry):
    registry.set_active("1.0.0")
    n_threads = 16
    barrier = threading.Barrier(n_threads)
    errors: list[Exception] = []

    def worker(offset: int):
        try:
            barrier.wait()
            seq = itertools.islice(itertools.cycle(VERSIONS), offset, offset + 40)
            for v in seq:
                registry.set_active(v)
                active = registry.get_active()
                assert active in VERSIONS, f"observado active corrompido/desconhecido: {active!r}"
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"erros de concorrência: {errors[:3]}"
    assert registry.get_active() in VERSIONS


def test_registry_endpoints(client, registry, monkeypatch):
    import app.levels.level5 as level5

    monkeypatch.setattr(level5, "_registry", registry, raising=False)

    assert {m["version"] for m in client.get("/models").json()["models"]} == set(VERSIONS)

    r = client.post("/models/active", json={"version": "1.1.0"})
    assert r.status_code == 200
    assert client.get("/models/active").json()["active"] == "1.1.0"

    assert client.post("/models/active", json={"version": "9.9.9"}).status_code == 404
