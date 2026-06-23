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

# Ferramentas que você vai precisar dentro dos métodos abaixo:
from ml.model_loader import load_yolo, model_id_from_weights  # noqa: F401
from ml.versioning import parse_model_filename  # noqa: F401


class ModelRegistry:
    """Descobre + serve modelos versionados de ``models_dir``.

    Thread-safety importa: ``set_active`` e os métodos de leitura podem ser chamados
    concorrentemente por muitas threads de request. Um leitor NUNCA deve observar um
    estado inconsistente (ex.: uma versão ativa cujo modelo ainda não foi carregado,
    ou ``None`` no meio de um swap). Carregue o novo modelo POR COMPLETO, e só então
    publique-o atomicamente.
    """

    def __init__(self, models_dir: Path = config.MODELS_DIR) -> None:
        self.models_dir = Path(models_dir)
        # TODO(candidate): inicialize seu estado (versão ativa, cache de modelos, um lock).
        raise NotImplementedError

    def discover(self) -> list[ModelInfo]:
        """Lista os artefatos versionados em ``models_dir``.

        Case os arquivos via ``parse_model_filename`` (ignore qualquer coisa que não
        case com a gramática). Retorne um ``ModelInfo`` por versão, com ``active``
        definido corretamente, ordenado por **ordem numérica SemVer** (compare MAJOR,
        MINOR, PATCH como inteiros — então 1.2.0 < 1.10.0, não lexicograficamente).
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def list_models(self) -> ModelList:
        """Retorna os modelos descobertos mais a versão ativa."""
        # TODO(candidate): implementar.
        raise NotImplementedError

    def get_active(self) -> str | None:
        """Retorna a string da versão ativa, ou None se nenhuma estiver definida."""
        # TODO(candidate): implementar.
        raise NotImplementedError

    def set_active(self, version: str) -> None:
        """Torna ``version`` ativa, fazendo hot-swap do modelo servido.

        Levante ``ValueError`` (ou ``KeyError``) se ``version`` for desconhecida.
        Carregue + faça cache do modelo de ``version`` (via ``load_yolo``) antes de
        publicá-la como ativa; carregar uma versão já em cache não deve recarregá-la.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def active_model(self):
        """Retorna o objeto de modelo carregado da versão ativa (ou None)."""
        # TODO(candidate): implementar.
        raise NotImplementedError

    def active_model_id(self) -> str | None:
        """Retorna o ``model_id_from_weights`` do artefato ativo, ou None."""
        # TODO(candidate): implementar.
        raise NotImplementedError
