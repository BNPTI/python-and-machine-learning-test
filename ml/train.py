"""Nível 4 — treino + persistência versionada.

Testes de aceitação:
  - ``tests/acceptance/test_level4_versioning.py``  (rápido, não precisa de GPU/torch)
  - ``tests/acceptance/test_level4_training.py``     (lento: fine-tune real em CPU)
"""

from __future__ import annotations

from pathlib import Path

from app import config
from app.schemas import ModelCard, TrainConfig

# Limites que o teste de aceitação garante no TrainConfig (mantém o tempo de CPU baixo).
MAX_EPOCHS = 20
MAX_IMGSZ = 640


def train(cfg: TrainConfig) -> str:
    """Requisitos:
    - fazer fine-tune do modelo base no dataset indicado por ``cfg``;
    - respeitar a configuração de treino de ``cfg`` (epochs, imgsz, batch, seed);
    - a execução deve ser reproduzível;
    - retornar o caminho do arquivo de pesos ``.pt`` produzido.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


def save_versioned_model(
    trained_weights: str,
    card: ModelCard,
    models_dir: Path = config.MODELS_DIR,
) -> Path:
    """Requisitos:
    - em ``models_dir``, escrever o arquivo de pesos versionado (cópia de
      ``trained_weights``) e, ao lado, o ``card`` serializado em JSON — ambos
      nomeados a partir do nome e da versão do card;
    - retornar o caminho do arquivo de pesos escrito;
    - ser I/O puro (não carregar o modelo).
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
