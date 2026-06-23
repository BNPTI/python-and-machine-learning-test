"""Aceitação do nível 2 — detecção de objetos.

Os testes de contrato + load-once usam um double FakeYOLO (determinístico, sem
torch). Um smoke test lento exercita o modelo real de ponta a ponta.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import app.levels.level2 as level2
from app import config
from ml.model_loader import model_id_from_weights
from tests.conftest import FakeYOLO

# (cls, confidence, [x1, y1, x2, y2]); algumas boxes deliberadamente fora dos limites.
DETS = [
    (0, 0.90, [-10.0, -5.0, 100.0, 120.0]),
    (1, 0.40, [600.0, 400.0, 999.0, 999.0]),
    (0, 0.70, [50.0, 50.0, 150.0, 150.0]),
]
NAMES = {0: "person", 1: "car"}
W, H = 640, 480


@pytest.fixture
def patched(monkeypatch):
    calls = {"n": 0}

    def fake_load(weights):
        calls["n"] += 1
        return FakeYOLO(DETS, NAMES)

    monkeypatch.setattr(level2, "load_yolo", fake_load)
    monkeypatch.setattr(level2, "_detector", None, raising=False)
    return calls


def _post(client, png_bytes, conf):
    return client.post(
        f"/detect?conf={conf}",
        files={"file": ("x.png", png_bytes(W, H), "image/png")},
    )


def test_detect_contract(client, png_bytes, patched):
    r = _post(client, png_bytes, 0.0)
    assert r.status_code == 200
    body = r.json()
    assert body["model_id"] == model_id_from_weights(config.YOLO_WEIGHTS)
    assert body["count"] == len(body["detections"]) == 3

    confs = [d["confidence"] for d in body["detections"]]
    assert confs == sorted(confs, reverse=True), "deve estar ordenado por confiança desc"
    for d in body["detections"]:
        assert 0.0 <= d["confidence"] <= 1.0
        x1, y1, x2, y2 = d["box"]
        assert 0 <= x1 <= x2 <= W
        assert 0 <= y1 <= y2 <= H
        assert d["label"] in NAMES.values()


def test_threshold_is_monotonic(client, png_bytes, patched):
    counts = []
    for conf in (0.0, 0.5, 0.95):
        r = _post(client, png_bytes, conf)
        assert r.status_code == 200
        counts.append(r.json()["count"])
    assert counts[0] >= counts[1] >= counts[2]
    assert counts == [3, 2, 0]


def test_model_loaded_at_most_once(client, png_bytes, patched):
    for _ in range(4):
        assert _post(client, png_bytes, 0.0).status_code == 200
    assert patched["n"] == 1, f"modelo construído {patched['n']}x; carregue uma vez e faça cache"


@pytest.mark.slow
def test_detect_real_smoke(client, monkeypatch):
    """Ponta a ponta com o modelo real (precisa de ultralytics + weights baixados)."""
    from tests.conftest import need

    need("ultralytics")
    if not Path(config.YOLO_WEIGHTS).exists():
        pytest.skip("rode `make fetch-weights` primeiro")
    if not config.SAMPLE_IMAGE.exists():
        pytest.skip("rode `make assets` primeiro")
    monkeypatch.setattr(level2, "_detector", None, raising=False)

    r = client.post(
        "/detect?conf=0.1",
        files={"file": ("s.png", config.SAMPLE_IMAGE.read_bytes(), "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    # Apenas contrato — NÃO fazemos assert de labels específicos numa imagem sintética.
    for d in body["detections"]:
        assert 0.0 <= d["confidence"] <= 1.0
        x1, y1, x2, y2 = d["box"]
        assert x1 <= x2 and y1 <= y2
