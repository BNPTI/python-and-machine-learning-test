"""Nível 1 — Fundamentos & FastAPI.

Implemente tudo o que estiver marcado com `TODO(candidate)`. Teste de aceitação:
``tests/acceptance/test_level1.py``. Rode com: ``make test-fast``.
"""

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.schemas import Box, HealthResponse, ImageMetadata

router = APIRouter(tags=["level1"])


def clamp_box(box: Box, width: int, height: int) -> Box:
    """Requisitos:
    - restringir uma bounding box ``[x1, y1, x2, y2]`` aos limites de uma imagem
      ``width`` × ``height``;
    - a box resultante deve estar inteiramente dentro da imagem e ser válida;
    - não modificar a entrada.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Requisitos:
    - retornar o status do serviço, sua identificação (nome e versão) e os níveis
      atualmente ativos na API.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.post("/image/metadata", response_model=ImageMetadata)
async def image_metadata(file: UploadFile) -> ImageMetadata:
    """Requisitos:
    - para um upload válido, retornar largura, altura, o modo de cor (sem converter
      a imagem) e o formato;
    - um upload que não seja uma imagem válida deve falhar de forma graciosa com
      HTTP 400.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
