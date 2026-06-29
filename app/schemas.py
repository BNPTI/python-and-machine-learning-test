"""Contratos de dados compartilhados por todo o desafio.

Estes modelos Pydantic são o *contrato* entre o seu código e os testes de
aceitação. Não renomeie campos nem mude seus tipos — os testes dependem deles.
Você pode adicionar novos modelos seus em outro lugar.

Convenção de coordenadas (usada em todos os lugares): bounding boxes e zonas
estão em coordenadas de PIXEL como ``[x1, y1, x2, y2]`` com ``x1 <= x2`` e
``y1 <= y2``, origem no canto superior esquerdo da imagem/frame.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

Box = list[float]  # [x1, y1, x2, y2] em pixels


# --------------------------------------------------------------------------- #
# Nível 1
# --------------------------------------------------------------------------- #
class HealthResponse(BaseModel):
    status: str = Field(description="literal 'ok' quando o serviço está no ar")
    service: str
    version: str
    levels: list[int] = Field(description="números dos níveis ligados ao app")


class ImageMetadata(BaseModel):
    width: int
    height: int
    mode: str = Field(description="modo da imagem PIL, ex.: 'RGB' (retorne tal e qual; não converta)")
    format: str | None = Field(default=None, description="formato PIL, ex.: 'PNG' (None se desconhecido)")


# --------------------------------------------------------------------------- #
# Nível 2 — detecção de objetos
# --------------------------------------------------------------------------- #
class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    box: Box = Field(description="[x1, y1, x2, y2] em pixels, limitado aos limites da imagem")


class DetectResponse(BaseModel):
    # 'model_id' começa com o prefixo protegido 'model_' do pydantic; libera ele.
    model_config = ConfigDict(protected_namespaces=())

    model_id: str = Field(description="identificador do modelo que produziu estas detecções")
    count: int
    detections: list[Detection]


# --------------------------------------------------------------------------- #
# Nível 3 — anomalia comportamental em vídeo
# --------------------------------------------------------------------------- #
class Zone(BaseModel):
    """Região retangular de interesse, em coordenadas de PIXEL."""

    x1: float
    y1: float
    x2: float
    y2: float


class AnomalyEvent(BaseModel):
    kind: str = Field(description="ex.: 'zone_intrusion'")
    start_frame: int = Field(description="índice do frame RAW onde o evento abriu")
    end_frame: int = Field(description="índice do frame RAW onde o evento fechou (inclusive)")
    start_time: float = Field(description="start_frame / fps, em segundos")
    end_time: float = Field(description="end_frame / fps, em segundos")
    peak_count: int = Field(description="máximo de alvos simultâneos dentro da zona durante o evento")


# --------------------------------------------------------------------------- #
# Nível 4 — treino / avaliação / versionamento
# --------------------------------------------------------------------------- #
class TrainConfig(BaseModel):
    data_yaml: str
    epochs: int = Field(gt=0)
    imgsz: int = Field(gt=0)
    batch: int = Field(gt=0)
    seed: int = 0
    base_weights: str = "yolov8n.pt"


class EvalMetrics(BaseModel):
    map50: float = Field(ge=0.0, le=1.0, description="mAP@0.5")
    map50_95: float = Field(ge=0.0, le=1.0, description="mAP@0.5:0.95")
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)


class LeakageCheck(BaseModel):
    method: str = Field(description="como a sobreposição foi calculada, ex.: 'sha256-of-pixels'")
    overlap_count: int = Field(ge=0, description="nº de imagens presentes em AMBOS train e val")


class ModelCard(BaseModel):
    name: str
    version: str = Field(description="MAJOR.MINOR.PATCH")
    task: str = "detect"
    classes: list[str]
    metrics: EvalMetrics
    train_config: TrainConfig
    dataset_hash: str = Field(description="sha256 hex do conjunto de treino")
    leakage_check: LeakageCheck
    base_weights: str
    framework: str
    created_at: str = Field(description="timestamp ISO-8601 UTC")


# --------------------------------------------------------------------------- #
# Nível 5 — registro / serving de modelos
# --------------------------------------------------------------------------- #
class ModelInfo(BaseModel):
    version: str
    path: str
    active: bool


class ModelList(BaseModel):
    active: str | None = None
    models: list[ModelInfo]


class SetActiveRequest(BaseModel):
    version: str
