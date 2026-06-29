"""Nível 2 — Detecção de objetos (consumir um modelo YOLO pré-treinado).

Teste de aceitação: ``tests/acceptance/test_level2.py``.

Construir o modelo é caro: ele deve ser construído no máximo uma vez e reutilizado
em todas as requisições, e não a cada chamada.
"""

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app import config
from app.schemas import Detection, DetectResponse
from ml.model_loader import load_yolo, model_id_from_weights  # noqa: F401

router = APIRouter(tags=["level2"])


class Detector:
    """Encapsula um modelo de detecção YOLO."""

    def __init__(self, weights: str = config.YOLO_WEIGHTS) -> None:
        self.weights = weights
        self.model_id = model_id_from_weights(weights)
        self._model = None

    def load(self) -> None:
        """Requisitos:
        - garantir que o modelo subjacente seja construído no máximo uma vez;
        - com o modelo já construído, uma nova chamada não deve reconstruí-lo.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def detect(self, image, conf: float) -> list[Detection]:
        """Requisitos:
        - executar a detecção na imagem recebida (já decodificada) e retornar as
          detecções, cada uma com rótulo, confiança e uma box restrita aos limites
          da imagem;
        - descartar detecções abaixo de ``conf`` (limiar inclusivo: igual a ``conf``
          é mantida);
        - ordenar o resultado da maior para a menor confiança.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError


def get_detector() -> Detector:
    """Requisitos:
    - retornar uma instância de ``Detector`` compartilhada por toda a aplicação;
    - criá-la e carregá-la apenas na primeira utilização, reutilizando-a depois, de
      modo que o modelo seja construído uma única vez no processo.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile, conf: float = 0.25) -> DetectResponse:
    """Requisitos:
    - ``conf`` (query param, default 0.25) é a confiança mínima;
    - retornar um ``DetectResponse`` com as detecções e o identificador do modelo;
    - um upload que não seja uma imagem válida deve falhar de forma graciosa.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
