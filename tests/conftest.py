"""Fixtures de teste compartilhadas + o test double FakeYOLO.

FORNECIDO — NÃO EDITE.

Este arquivo é mantido leve em dependências no import (sem numpy/cv2/torch) para
que os testes de nível 1 e de wiring sejam coletados mesmo antes da stack
completa estar instalada.

Correção (grading) vs auto-teste
--------------------------------
``need("ultralytics")`` pula um teste quando a dependência está ausente —
conveniente enquanto você itera. No ambiente oficial de correção definimos
``FG_REQUIRE_ML=1`` para que uma dependência ausente vire uma falha DURA (um
nível nunca deve passar por ser pulado silenciosamente).
"""

from __future__ import annotations

import io
import os

import pytest

REQUIRE_ML = os.environ.get("FG_REQUIRE_ML") == "1"


def need(module: str):
    """Importa uma dependência pesada; pula localmente, falha dura sob FG_REQUIRE_ML=1."""
    if REQUIRE_ML:
        return __import__(module)
    return pytest.importorskip(module)


# --------------------------------------------------------------------------- #
# FakeYOLO — imita a fatia da API do Ultralytics que o contrato do nível 2 usa.
# --------------------------------------------------------------------------- #
class FakeArr(list):
    """Substituto mínimo de um tensor/ndarray que suporta ``.tolist()``."""

    def tolist(self):  # noqa: D401
        return [x.tolist() if isinstance(x, FakeArr) else x for x in self]


class FakeBox:
    def __init__(self, xyxy, conf, cls):
        self.xyxy = FakeArr([FakeArr(list(xyxy))])
        self.conf = FakeArr([float(conf)])
        self.cls = FakeArr([int(cls)])


class FakeResults:
    def __init__(self, boxes, names):
        self.boxes = boxes
        self.names = names


class FakeYOLO:
    """Um callable que retorna detecções fixas independente da imagem de entrada."""

    def __init__(self, detections, names):
        # detections: lista de (cls:int, conf:float, [x1,y1,x2,y2])
        self._boxes = [FakeBox(b, c, k) for (k, c, b) in detections]
        self._names = names

    def __call__(self, *args, **kwargs):
        return [FakeResults(self._boxes, self._names)]

    def predict(self, *args, **kwargs):
        return self(*args, **kwargs)


@pytest.fixture
def app():
    from app.main import app as _app

    return _app


@pytest.fixture
def client(app):
    need("httpx")  # TestClient precisa de httpx
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def png_bytes():
    """Retorna uma factory que constrói um PNG RGB em memória de um dado tamanho."""

    def _make(width: int = 640, height: int = 480) -> bytes:
        need("PIL")  # pula o teste localmente se o Pillow não estiver instalado
        from PIL import Image as PILImage

        buf = io.BytesIO()
        PILImage.new("RGB", (width, height), (50, 60, 70)).save(buf, format="PNG")
        return buf.getvalue()

    return _make
