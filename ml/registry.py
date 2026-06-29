"""Nível 5 — registry de modelos com hot-swap em runtime.

Teste de aceitação: ``tests/acceptance/test_level5.py``.

Um ``ModelRegistry`` descobre artefatos versionados em ``models/`` (escritos pelo
nível 4), rastreia qual versão está *ativa*, carrega + faz cache de cada modelo de
forma preguiçosa (lazy), e permite trocar a versão ativa em runtime — com segurança,
sob concorrência.
"""

from __future__ import annotations

from pathlib import Path

from app import config
from app.schemas import ModelInfo, ModelList

from ml.model_loader import load_yolo, model_id_from_weights  # noqa: F401
from ml.versioning import parse_model_filename  # noqa: F401


class ModelRegistry:
    """Descobre e serve modelos versionados de ``models_dir``.

    Requisito de thread-safety: ``set_active`` e os métodos de leitura podem ser
    chamados concorrentemente por várias threads; um leitor nunca deve observar um
    estado inconsistente.
    """

    def __init__(self, models_dir: Path = config.MODELS_DIR) -> None:
        self.models_dir = Path(models_dir)
        # TODO(candidate): implementar.
        raise NotImplementedError

    def discover(self) -> list[ModelInfo]:
        """Requisitos:
        - listar os artefatos versionados em ``models_dir``, um por versão,
          indicando qual é a ativa;
        - ordenar por versão em ordem numérica (não lexicográfica).
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def list_models(self) -> ModelList:
        """Requisitos:
        - retornar os modelos descobertos junto com a versão ativa.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def get_active(self) -> str | None:
        """Requisitos:
        - retornar a versão ativa, ou None se nenhuma estiver definida.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def set_active(self, version: str) -> None:
        """Requisitos:
        - tornar ``version`` a versão ativa; uma versão desconhecida deve gerar erro
          (ValueError);
        - o modelo da versão deve ser carregado e mantido em cache antes de se tornar
          ativo;
        - uma versão já em cache não deve ser recarregada.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def active_model(self):
        """Requisitos:
        - retornar o objeto de modelo carregado da versão ativa, ou None.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def active_model_id(self) -> str | None:
        """Requisitos:
        - retornar o identificador do artefato ativo, ou None.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError
