"""Nível 5 — endpoints do registro de modelos (finos).

O trabalho de verdade é o ``ModelRegistry`` em ``ml/registry.py``. Estes
endpoints são FORNECIDOS e passam a funcionar assim que o registro for
implementado. O registro é criado de forma lazy para que importar o app nunca
falhe enquanto ele ainda é um stub.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import ModelList, SetActiveRequest
from ml.registry import ModelRegistry

router = APIRouter(tags=["level5"])

_registry: ModelRegistry | None = None


def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


@router.get("/models", response_model=ModelList)
def list_models() -> ModelList:
    return get_registry().list_models()


@router.get("/models/active")
def get_active() -> dict:
    reg = get_registry()
    return {"active": reg.get_active(), "model_id": reg.active_model_id()}


@router.post("/models/active", response_model=ModelList)
def set_active(req: SetActiveRequest) -> ModelList:
    reg = get_registry()
    try:
        reg.set_active(req.version)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=404, detail=f"versão de modelo desconhecida: {req.version}") from exc
    return reg.list_models()
