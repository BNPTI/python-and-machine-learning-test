"""Nível 4 — avaliação + governança de dataset.

Os testes de aceitação ficam em ``tests/acceptance/test_level4_*``.

``evaluate`` exige um modelo treinado (teste lento); ``compute_dataset_hash`` e
``check_leakage`` não dependem de treino (teste rápido).
"""

from __future__ import annotations

from pathlib import Path

from app.schemas import EvalMetrics, LeakageCheck


def evaluate(weights: str, data_yaml: str, imgsz: int) -> EvalMetrics:
    """Requisitos:
    - avaliar ``weights`` no split de validação declarado em ``data_yaml``;
    - retornar as métricas de detecção (map50, map50_95, precision, recall) como
      floats em ``[0, 1]``.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def compute_dataset_hash(images_dir: str | Path) -> str:
    """Requisitos:
    - retornar um digest sha256 hex estável (64 chars) sobre um conjunto de imagens;
    - ser determinístico: o mesmo conjunto produz sempre o mesmo valor; adicionar,
      remover ou alterar uma imagem deve mudá-lo.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def check_leakage(train_images_dir: str | Path, val_images_dir: str | Path) -> LeakageCheck:
    """Requisitos:
    - detectar imagens presentes em AMBOS os splits de treino e validação;
    - reportar quantas se sobrepõem (``overlap_count`` é 0 para um split limpo) e
      registrar em ``method`` como a comparação foi feita.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
