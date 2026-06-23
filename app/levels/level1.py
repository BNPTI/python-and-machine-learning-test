"""Nível 1 — Fundamentos & FastAPI.

Um Nível 1–3 bem-feito já é um forte sinal de contratação. NÃO avance correndo
para os níveis posteriores em detrimento de deixar os primeiros limpos e
corretos.

Implemente tudo o que estiver marcado com `TODO(candidate)`. Teste de aceitação:
``tests/acceptance/test_level1.py``. Rode com: ``make test-fast``.
"""

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.schemas import Box, HealthResponse, ImageMetadata

router = APIRouter(tags=["level1"])


def clamp_box(box: Box, width: int, height: int) -> Box:
    """Limita uma box ``[x1, y1, x2, y2]`` aos limites da imagem.

    Requisitos:
      - limitar cada coordenada a ``[0, width]`` (x) / ``[0, height]`` (y);
      - a box retornada deve satisfazer ``x1 <= x2`` e ``y1 <= y2`` (normalize
        se a entrada estiver invertida);
      - retornar uma nova lista de 4 floats; não mutar a entrada.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe.

    Retorne ``status="ok"`` mais o nome/versão do serviço e os níveis ligados
    (use ``app.config.SERVICE_NAME``, ``SERVICE_VERSION``, ``LEVELS``).
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.post("/image/metadata", response_model=ImageMetadata)
async def image_metadata(file: UploadFile) -> ImageMetadata:
    """Retorna metadados básicos de uma imagem enviada.

    Leia os bytes enviados, abra-os com Pillow e retorne width, height,
    ``mode`` (retorne o ``img.mode`` do PIL tal e qual — NÃO converta a imagem) e
    ``format`` (ex.: "PNG"; None se desconhecido). Decodifique a imagem apenas
    uma vez. Trate um upload que não seja imagem de forma graciosa (HTTP 400, não
    um 500).
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
