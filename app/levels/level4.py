"""Nível 4 — router de treino (fino).

O trabalho de verdade do nível 4 está em ``ml/train.py`` e ``ml/evaluate.py``.
Este router apenas expõe a receita de treino recomendada para que ela seja
descobrível pela API. FORNECIDO.
"""

from __future__ import annotations

from fastapi import APIRouter

from app import config
from app.schemas import TrainConfig
from ml.train import MAX_EPOCHS, MAX_IMGSZ

router = APIRouter(tags=["level4"])


@router.get("/level4/recommended-config", response_model=TrainConfig)
def recommended_config() -> TrainConfig:
    """A receita de treino que recomendamos para o dataset sintético de shapes.

    Mantenha-se dentro dos limites (epochs <= {max_epochs}, imgsz <= {max_imgsz})
    para que uma execução em CPU fique na faixa de minutos.
    """
    return TrainConfig(
        data_yaml=str(config.SHAPES_DATA_YAML),
        epochs=min(8, MAX_EPOCHS),
        imgsz=min(416, MAX_IMGSZ),
        batch=16,
        seed=0,
        base_weights=config.YOLO_WEIGHTS,
    )
