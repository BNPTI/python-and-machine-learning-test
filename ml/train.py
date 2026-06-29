"""Nível 4 — treino + persistência versionada.

Testes de aceitação:
  - ``tests/acceptance/test_level4_versioning.py``  (rápido, não precisa de GPU/torch)
  - ``tests/acceptance/test_level4_training.py``     (lento: fine-tune real em CPU)

Implemente os blocos de construção abaixo. O teste de treino os conecta:
``train`` -> ``evaluate`` -> montar um ``ModelCard`` -> ``save_versioned_model``.
"""

from __future__ import annotations

from pathlib import Path

from app import config
from app.schemas import ModelCard, TrainConfig

# Limites que o teste de aceitação garante no TrainConfig (mantém o tempo de CPU baixo).
MAX_EPOCHS = 20
MAX_IMGSZ = 640


def train(cfg: TrainConfig) -> str:
    """Faz fine-tune de ``cfg.base_weights`` em ``cfg.data_yaml`` e retorna o caminho
    para os melhores pesos treinados (ex.: o ``best.pt`` que o Ultralytics escreve).

    Requisitos:
      - respeitar ``cfg.epochs``, ``cfg.imgsz``, ``cfg.batch`` e ``cfg.seed``;
      - tornar a execução reproduzível (defina a seed; prefira configurações determinísticas);
      - retornar um caminho de filesystem para os pesos ``.pt`` produzidos.

    Dica: ``yolo = load_yolo(cfg.base_weights); yolo.train(data=..., epochs=...)``.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def save_versioned_model(
    trained_weights: str,
    card: ModelCard,
    models_dir: Path = config.MODELS_DIR,
) -> Path:
    """Persiste um modelo treinado como artefato versionado + seu model card.

    Escreve dois arquivos irmãos em ``models_dir``:
      - ``<card.name>-v<card.version>.pt``  (cópia de ``trained_weights``)
      - ``<card.name>-v<card.version>.json`` (``card`` serializado)

    Use ``ml.versioning.model_filename`` para o nome do ``.pt``. Retorne o caminho
    do ``.pt`` escrito. Isto deve funcionar sem carregar o modelo (I/O puro).
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
