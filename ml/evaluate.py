"""Nível 4 — avaliação + governança de dataset.

Os testes de aceitação ficam em ``tests/acceptance/test_level4_*``.

``evaluate`` precisa de um modelo treinado (teste lento). ``compute_dataset_hash`` e
``check_leakage`` são operações puras de arquivo (teste rápido) — elas verificam se
você entende *governança* de avaliação, não apenas chamar ``model.val()``.
"""

from __future__ import annotations

from pathlib import Path

from app.schemas import EvalMetrics, LeakageCheck


def evaluate(weights: str, data_yaml: str, imgsz: int) -> EvalMetrics:
    """Avalia ``weights`` no split de validação declarado em ``data_yaml``.

    Roda a validação (``load_yolo(weights).val(data=data_yaml, imgsz=imgsz)``) e
    mapeia os resultados para ``EvalMetrics`` (map50, map50_95, precision, recall).
    Os quatro devem ser floats em ``[0, 1]``.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def compute_dataset_hash(images_dir: str | Path) -> str:
    """Retorna um digest hex sha256 estável (64 chars) sobre as imagens de treino.

    Faça o hash do conjunto de imagens de forma determinística (ex.: ordene por nome
    de arquivo, agregue os bytes de cada arquivo em um único sha256). Regenerar o
    dataset com a mesma seed deve produzir o mesmo digest; adicionar/remover uma
    imagem deve alterá-lo.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def check_leakage(train_images_dir: str | Path, val_images_dir: str | Path) -> LeakageCheck:
    """Detecta imagens que aparecem em AMBOS train e val (vazamento de dados).

    Compare os dois splits por hash de conteúdo e reporte quantas imagens se
    sobrepõem. Para um split limpo, ``overlap_count`` é 0. Defina ``method`` para
    descrever como você comparou (ex.: ``"sha256-of-file-bytes"``).
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
