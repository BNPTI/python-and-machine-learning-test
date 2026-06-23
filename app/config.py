"""Configuração de runtime. Lê variáveis de ambiente com defaults sensatos.

FORNECIDO — você não deve precisar editar isto.
"""

from __future__ import annotations

import os
from pathlib import Path

# Raiz do repositório (…/candidates/test).
ROOT = Path(__file__).resolve().parent.parent

SERVICE_NAME = "faceguard-ml-challenge"
SERVICE_VERSION = "0.1.0"

# Pesos do detector pré-treinado (baixados por `make setup`).
YOLO_WEIGHTS = os.environ.get("FG_YOLO_WEIGHTS", "yolov8n.pt")

# Onde o nível 4 grava artefatos versionados de modelo e onde o nível 5 os descobre.
MODELS_DIR = ROOT / "models"

# Fixtures geradas (produzidas por `make assets`).
DATA_DIR = ROOT / "data"
SAMPLE_IMAGE = DATA_DIR / "images" / "sample.png"
SAMPLE_VIDEO = DATA_DIR / "video" / "sample.mp4"
SHAPES_DATASET = DATA_DIR / "datasets" / "shapes"
SHAPES_DATA_YAML = SHAPES_DATASET / "data.yaml"

# Níveis atualmente ligados ao app (usados por /health).
LEVELS = [1, 2, 3, 4, 5]
