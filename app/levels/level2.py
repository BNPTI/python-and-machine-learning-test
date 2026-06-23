"""Nível 2 — Detecção de objetos (consumir um modelo YOLO pré-treinado).

Teste de aceitação: ``tests/acceptance/test_level2.py``.

O modelo é caro de construir. Construa-o **uma única vez** (via ``load_yolo``) e
reutilize-o em toda requisição — o teste de aceitação substitui ``load_yolo`` por
um contador e verifica que ele roda no máximo uma vez ao longo de muitas chamadas
``/detect``.
"""

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app import config
from app.schemas import Detection, DetectResponse
from ml.model_loader import load_yolo, model_id_from_weights  # noqa: F401  (use load_yolo em load())

router = APIRouter(tags=["level2"])


class Detector:
    """Encapsula um modelo YOLO. Carrega os pesos sob demanda e os cacheia."""

    def __init__(self, weights: str = config.YOLO_WEIGHTS) -> None:
        self.weights = weights
        self.model_id = model_id_from_weights(weights)
        self._model = None

    def load(self) -> None:
        """Constrói o modelo subjacente exatamente uma vez.

        Chame ``load_yolo(self.weights)`` e guarde o resultado em ``self._model``.
        Chamar ``load()`` de novo quando já carregado deve ser um no-op (NÃO
        construa um segundo modelo).
        """
        # TODO(candidate): implementar.
        raise NotImplementedError

    def detect(self, image, conf: float) -> list[Detection]:
        """Roda a detecção em uma imagem e retorna detecções parseadas e filtradas.

        ``image`` é um ``Image`` do Pillow (já decodificado pelo endpoint).

        Passos:
          1. garanta que o modelo está carregado;
          2. rode a inferência (o padrão canônico do Ultralytics funciona tanto no
             modelo real quanto no test double dos testes)::

                 results = self._model(image, verbose=False)
                 r = results[0]
                 names = r.names                       # dict[int, str]
                 for box in r.boxes:
                     xyxy  = box.xyxy[0].tolist()       # [x1, y1, x2, y2]
                     score = float(box.conf[0])
                     cls   = int(box.cls[0])
                     label = names[cls]

          3. limite cada box aos limites da imagem (reutilize o ``clamp_box`` do
             nível 1);
          4. descarte detecções com ``score < conf`` (uma detecção com
             ``score == conf`` é MANTIDA);
          5. retorne-as ordenadas por confiança, da maior para a menor.
        """
        # TODO(candidate): implementar.
        raise NotImplementedError


# Singleton de processo para que o modelo seja carregado UMA vez para todo o app.
_detector: Detector | None = None


def get_detector() -> Detector:
    """Retorna o ``Detector`` compartilhado, construindo + carregando no primeiro uso.

    Use a global de módulo ``_detector``: construa um ``Detector`` e chame
    ``.load()`` na primeira vez, depois reutilize-o. ``/detect`` (e o teste de
    aceitação) chamam isto; deve disparar exatamente uma construção de modelo ao
    longo de todas as requisições.
    """
    # TODO(candidate): implementar o singleton lazy.
    raise NotImplementedError


@router.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile, conf: float = 0.25) -> DetectResponse:
    """Detecta objetos em uma imagem enviada.

    O query param ``conf`` é a confiança mínima (default 0.25). Decodifique o
    upload uma vez (Pillow), rode ``get_detector().detect(image, conf)`` e retorne
    um ``DetectResponse`` cujo ``model_id`` é o ``model_id`` do detector.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError
