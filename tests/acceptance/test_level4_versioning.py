"""Aceitação do nível 4 (rápida) — versionamento + governança de dataset.

Não precisa de GPU/torch: são operações puras de arquivo. Verificam as partes do
nível 4 que carregam o sinal de mid-level (versionamento de artefato, model card,
consciência de vazamento de dados) independentemente do treino lento.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.schemas import EvalMetrics, LeakageCheck, ModelCard, TrainConfig
from ml.evaluate import check_leakage, compute_dataset_hash
from ml.train import save_versioned_model
from ml.versioning import MODEL_FILENAME_RE, is_semver

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _card(version="1.0.0") -> ModelCard:
    return ModelCard(
        name="shapes-detector",
        version=version,
        task="detect",
        classes=["circle", "square", "triangle"],
        metrics=EvalMetrics(map50=0.82, map50_95=0.55, precision=0.78, recall=0.71),
        train_config=TrainConfig(
            data_yaml="data/datasets/shapes/data.yaml",
            epochs=8,
            imgsz=416,
            batch=16,
            seed=0,
            base_weights="yolov8n.pt",
        ),
        dataset_hash="a" * 64,
        leakage_check=LeakageCheck(method="sha256-of-file-bytes", overlap_count=0),
        base_weights="yolov8n.pt",
        framework="ultralytics",
        created_at="2026-06-22T00:00:00Z",
    )


def test_save_versioned_model_writes_artifact_and_card(tmp_path):
    trained = tmp_path / "best.pt"
    trained.write_bytes(b"FAKE-WEIGHTS")
    models_dir = tmp_path / "models"

    out = Path(save_versioned_model(str(trained), _card("1.0.0"), models_dir=models_dir))

    assert out.exists()
    assert out.name == "shapes-detector-v1.0.0.pt"
    assert MODEL_FILENAME_RE.match(out.name)

    card_path = out.with_suffix(".json")
    assert card_path.exists(), "um model card irmão <name>-v<ver>.json deve ser escrito"
    loaded = ModelCard.model_validate_json(card_path.read_text())
    assert loaded.version == "1.0.0" and is_semver(loaded.version)
    assert HEX64.match(loaded.dataset_hash)
    assert loaded.metrics.map50 <= 1.0


def test_check_leakage_clean(tmp_path):
    train_dir, val_dir = tmp_path / "train", tmp_path / "val"
    train_dir.mkdir()
    val_dir.mkdir()
    (train_dir / "a.png").write_bytes(b"image-A")
    (train_dir / "b.png").write_bytes(b"image-B")
    (val_dir / "c.png").write_bytes(b"image-C")

    result = check_leakage(train_dir, val_dir)
    assert result.overlap_count == 0
    assert result.method


def test_check_leakage_detects_overlap(tmp_path):
    train_dir, val_dir = tmp_path / "train", tmp_path / "val"
    train_dir.mkdir()
    val_dir.mkdir()
    (train_dir / "a.png").write_bytes(b"same-bytes")
    (val_dir / "copy.png").write_bytes(b"same-bytes")  # conteúdo idêntico => vazamento

    assert check_leakage(train_dir, val_dir).overlap_count >= 1


def test_dataset_hash_is_stable_and_distinct():
    from app import config

    train_dir = config.SHAPES_DATASET / "images" / "train"
    val_dir = config.SHAPES_DATASET / "images" / "val"
    if not train_dir.exists():
        pytest.skip("rode `make assets` primeiro")

    h1 = compute_dataset_hash(train_dir)
    h2 = compute_dataset_hash(train_dir)
    assert HEX64.match(h1)
    assert h1 == h2, "o hash deve ser determinístico"
    assert compute_dataset_hash(val_dir) != h1, "dados diferentes => hash diferente"
