"""Ponto de entrada da aplicação FastAPI.

FORNECIDO — liga o router de cada nível em um único app. Você implementa os
routers em ``app/levels/levelN.py``. Rode com ``make run`` e explore em /docs.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.levels import level1, level2, level3, level4, level5

app = FastAPI(
    title="Face Guard AI/ML Challenge",
    version="0.1.0",
    description="Implemente os níveis descritos no README.md.",
)

app.include_router(level1.router)
app.include_router(level2.router)
app.include_router(level3.router)
app.include_router(level4.router)
app.include_router(level5.router)
