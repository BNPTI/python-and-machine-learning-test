"""Aceitação do nível 4 (lenta) — fine-tuning real no conjunto sintético de shapes.

Isto de fato treina na CPU, então está marcado como ``slow`` (minutos). Rode com
``make test`` (ou ``pytest -m slow``). O "piso" de mAP é CONSULTIVO: ele emite um
warning em vez de falhar, porque um treino minúsculo na CPU sobre um conjunto
minúsculo é estocástico. Os asserts duros são que o pipeline RODA e produz um
artefato válido.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from app.schemas import EvalMetrics, LeakageCheck, ModelCard, TrainConfig
from ml.evaluate import evaluate
from ml.train import MAX_EPOCHS, MAX_IMGSZ, save_versioned_model, train
from ml.versioning import MODEL_FILENAME_RE
from tests.conftest import need

ADVISORY_MAP50_FLOOR = 0.30  # "melhor que aleatório"; calibre antes de shippar


@pytest.mark.slow
def test_training_pipeline_end_to_end(tmp_path):
    need("ultralytics")
    need("torch")
    from app import config

    if not config.SHAPES_DATA_YAML.exists():
        pytest.skip("rode `make assets` primeiro")
    if not Path(config.YOLO_WEIGHTS).exists():
        pytest.skip("rode `make fetch-weights` primeiro")

    cfg = TrainConfig(
        data_yaml=str(config.SHAPES_DATA_YAML),
        epochs=3,
        imgsz=320,
        batch=16,
        seed=0,
        base_weights=config.YOLO_WEIGHTS,
    )
    # Checagem determinística de cap de config (substitui um assert flaky de wall-clock).
    assert cfg.epochs <= MAX_EPOCHS and cfg.imgsz <= MAX_IMGSZ

    weights = Path(train(cfg))
    assert weights.exists(), "train() deve retornar um caminho para os weights produzidos"

    metrics = evaluate(str(weights), cfg.data_yaml, cfg.imgsz)
    assert isinstance(metrics, EvalMetrics)
    for v in (metrics.map50, metrics.map50_95, metrics.precision, metrics.recall):
        assert 0.0 <= v <= 1.0

    # Piso consultivo — emite warning, não falha.
    if metrics.map50 < ADVISORY_MAP50_FLOOR:
        warnings.warn(
            f"mAP50={metrics.map50:.3f} < piso consultivo {ADVISORY_MAP50_FLOOR}; "
            "verifique a receita de treino / augmentation / seed.",
            stacklevel=1,
        )

    card = ModelCard(
        name="shapes-detector",
        version="1.0.0",
        task="detect",
        classes=["circle", "square", "triangle"],
        metrics=metrics,
        train_config=cfg,
        dataset_hash="0" * 64,
        leakage_check=LeakageCheck(method="sha256-of-file-bytes", overlap_count=0),
        base_weights=config.YOLO_WEIGHTS,
        framework="ultralytics",
        created_at="2026-06-22T00:00:00Z",
    )
    out = Path(save_versioned_model(str(weights), card, models_dir=tmp_path / "models"))
    assert out.exists()
    assert MODEL_FILENAME_RE.match(out.name)
    assert out.with_suffix(".json").exists()
