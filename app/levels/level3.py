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
    """Varre um vídeo e retorna eventos de intrusão em zona / loitering.

    Contrato (estas convenções são verificadas pelo teste de aceitação):

    Seleção de frames
      - Itere os frames RAW ``0, 1, 2, …``. *Processe* (rode o detector) apenas
        a cada ``frame_skip``-ésimo frame, isto é, índices RAW onde
        ``index % frame_skip == 0``. Exemplo: 10 frames, ``frame_skip=3`` ⇒ você
        processa os frames RAW ``{0, 3, 6, 9}`` (4 frames processados).

    Teste de dentro-da-zona
      - Uma detecção está "na zona" se o CENTRO da sua box
        ``((x1+x2)/2, (y1+y2)/2)`` está dentro de ``zone`` (bordas inclusivas).
      - ``in_zone_count`` para um frame processado = número de detecções na zona.

    Evento (run com debounce)
      - Um evento é uma sequência máxima de frames *processados* CONSECUTIVOS cada
        um com ``in_zone_count >= 1``, cujo comprimento é ``>= min_consecutive``.
      - Um frame processado com ``in_zone_count == 0`` encerra a sequência atual.
      - Sequências mais curtas que ``min_consecutive`` são ruído e NÃO emitem nada
        (blips de um único frame não devem disparar).
      - ``start_frame`` / ``end_frame`` são os índices RAW do primeiro / último
        frame processado da sequência (``end_frame`` inclusive).
      - ``start_time = start_frame / fps``, ``end_time = end_frame / fps``.
      - ``peak_count`` = máximo ``in_zone_count`` observado durante a sequência.

    Fim do vídeo
      - Se uma sequência qualificada (comprimento ``>= min_consecutive``) ainda
        estiver aberta quando o vídeo terminar, FAÇA o flush dela como um evento
        (fechado no último frame processado). Uma sequência aberta ainda abaixo de
        ``min_consecutive`` no EOF não emite nada.

    fps
      - Leia do vídeo; se indisponível/zero, use ``fallback_fps``.

    Exemplo resolvido
      - 10 frames, ``frame_skip=3`` ⇒ processados {0,3,6,9}. Se os frames {3,6,9}
        estão na zona e {0} não está, com ``min_consecutive=3`` ⇒ UM evento
        ``start_frame=3, end_frame=9``. Se apenas o frame {0} está na zona ⇒ nenhum
        evento.
    """
    # TODO(candidate): implementar. Abra o vídeo com cv2.VideoCapture, leia os
    # frames sequencialmente, aplique a regra de frame-skip, rode `detector.detect`,
    # mantenha a sequência com debounce e faça o flush no EOF.
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
