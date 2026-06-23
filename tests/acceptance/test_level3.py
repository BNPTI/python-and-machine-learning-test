"""Aceitação do nível 3 — detecção de anomalia por intrusão em zona, em vídeo.

Roda o ``analyze_video`` do candidato sobre o vídeo sintético entregue com o
``SimpleColorDetector`` fornecido (determinístico). Os asserts de janela usam uma
tolerância de ±1 frame; a contagem de eventos + o comportamento de debounce são
exatos.

Cenário entregue (ver scripts/generate_assets.py): 320x240 @ 10 fps, 120 frames,
marcador branco. Com frame_skip=4, min_consecutive=3 a timeline esperada é:
  - intrusão #1: frames brutos 20..60
  - blip de um único frame em 80  -> suprimido (run length 1 < 3)
  - intrusão #2: frames brutos 92..116, aberta no EOF -> flushed
=> exatamente DOIS eventos.
"""

from __future__ import annotations

import pytest

from app.levels.level3 import analyze_video
from app.schemas import Zone
from tests.conftest import need

# Constantes do cenário (espelham scripts/generate_assets.py).
ZONE = Zone(x1=110, y1=70, x2=210, y2=170)
FPS = 10
FRAME_SKIP = 4
MIN_CONSECUTIVE = 3


class _CountingDetector:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def detect(self, frame):
        self.calls += 1
        return self.inner.detect(frame)


@pytest.fixture
def detector():
    need("cv2")
    need("numpy")
    from app import config

    if not config.SAMPLE_VIDEO.exists():
        pytest.skip("rode `make assets` primeiro")
    from ml.detectors import SimpleColorDetector

    return _CountingDetector(SimpleColorDetector(target_rgb=(255, 255, 255), tol=70, min_area=150))


def _run(detector):
    from app import config

    return analyze_video(
        str(config.SAMPLE_VIDEO),
        detector,
        zone=ZONE,
        frame_skip=FRAME_SKIP,
        min_consecutive=MIN_CONSECUTIVE,
    )


def test_event_count_and_windows(detector):
    events = sorted(_run(detector), key=lambda e: e.start_frame)
    assert len(events) == 2, f"esperava 2 eventos (blip suprimido), obteve {len(events)}"

    e1, e2 = events
    assert abs(e1.start_frame - 20) <= 1 and abs(e1.end_frame - 60) <= 1
    assert abs(e2.start_frame - 92) <= 1 and abs(e2.end_frame - 116) <= 1
    for e in events:
        assert e.kind == "zone_intrusion"
        assert e.peak_count >= 1
        assert e.start_time == pytest.approx(e.start_frame / FPS, abs=0.2)
        assert e.end_time == pytest.approx(e.end_frame / FPS, abs=0.2)


def test_blip_is_suppressed(detector):
    # Nenhum evento deve ser um frame solitário em torno do blip do frame 80.
    events = _run(detector)
    assert all(not (78 <= e.start_frame <= 82 and e.end_frame - e.start_frame < 8) for e in events)


def test_frame_skip_respected(detector):
    _run(detector)
    # 120 frames, processa a cada 4 -> índices {0,4,…,116} = 30 chamadas do detector.
    assert detector.calls == 30, f"detector rodou {detector.calls}x; esperava 30 (frame_skip=4)"
