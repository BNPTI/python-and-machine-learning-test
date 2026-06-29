"""Nível 3 — Detecção de anomalia comportamental em vídeo.

Uma máquina de estados temporal com frame-skipping e tratamento de fim de vídeo.

Teste de aceitação: ``tests/acceptance/test_level3.py``.

A função é agnóstica ao detector: ``detector`` é qualquer coisa com um método
``detect(frame_bgr) -> list[Detection]`` que recebe UM argumento posicional — um
frame BGR do cv2 (numpy array) — e nenhum argumento de confiança. O teste de
aceitação injeta o ``SimpleColorDetector`` fornecido. (Nota: o seu ``Detector.detect`` do
nível 2 tem uma assinatura diferente — ``detect(image: PIL.Image, conf)`` — então
ele NÃO é um drop-in aqui; você o envolveria num pequeno adaptador para usá-lo em
footage real.)
"""

from __future__ import annotations

import cv2
from fastapi import APIRouter

from app import config
from app.schemas import AnomalyEvent, Zone
from ml.detectors import SimpleColorDetector

router = APIRouter(tags=["level3"])


def analyze_video(
    video_path: str,
    detector,
    *,
    zone: Zone,
    frame_skip: int = 1,
    min_consecutive: int = 3,
    kind: str = "zone_intrusion",
    fallback_fps: float = 25.0,
) -> list[AnomalyEvent]:
    """Requisitos — varrer um vídeo e retornar os eventos de intrusão em zona:
    - apenas os frames cujo índice é múltiplo de ``frame_skip`` são processados; os
      demais são pulados;
    - uma detecção está "na zona" quando o centro da sua box cai dentro de ``zone``
      (bordas inclusivas);
    - um evento é uma sequência máxima de frames processados consecutivos, cada um
      com ao menos uma detecção na zona, cujo comprimento seja ``>= min_consecutive``;
      sequências mais curtas não geram evento;
    - cada evento registra o frame e o instante (derivado do fps) de início e de
      fim, e o pico de detecções simultâneas na zona durante a sequência;
    - uma sequência qualificada ainda aberta no fim do vídeo deve ser emitida;
    - o fps é obtido do vídeo; se indisponível, usar ``fallback_fps``.
    """
    # TODO(candidate): implementar.
    raise NotImplementedError


@router.get("/video/analyze", response_model=list[AnomalyEvent])
def analyze_sample_video(
    frame_skip: int = 4, min_consecutive: int = 3
) -> list[AnomalyEvent]:
    """Endpoint de demo — roda o seu ``analyze_video`` no vídeo de exemplo incluído.

    FORNECIDO por conveniência (te dá uma superfície de API funcional assim que o
    ``analyze_video`` estiver pronto). Usa o ``SimpleColorDetector`` verde genérico
    e uma zona centralizada; o teste de aceitação exercita ``analyze_video``
    diretamente, não este endpoint.
    """
    cap = cv2.VideoCapture(str(config.SAMPLE_VIDEO))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 320
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 240
    cap.release()
    zone = Zone(x1=width * 0.25, y1=height * 0.25, x2=width * 0.75, y2=height * 0.75)
    detector = SimpleColorDetector(target_rgb=(255, 255, 255), label="marker")
    return analyze_video(
        str(config.SAMPLE_VIDEO),
        detector,
        zone=zone,
        frame_skip=frame_skip,
        min_consecutive=min_consecutive,
    )
