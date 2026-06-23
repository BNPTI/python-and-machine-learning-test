"""O único ponto de entrada documentado para construir um modelo YOLO.

FORNECIDO — NÃO EDITE (arquivo protegido, veja scripts/check_integrity.py).

Por que isto existe
-------------------
Construir um detector é caro (carrega os pesos do disco para a memória).
Um serviço correto o constrói **uma única vez** e o reutiliza entre requests.

Este módulo é a *costura* (seam) que permite aos avaliadores verificar essa
propriedade sem mexer nas entranhas do Ultralytics: chame ``load_yolo(...)``
exatamente uma vez no seu código, faça cache do resultado e reutilize. O teste
de aceitação do nível 2 substitui esta função por um contador e garante que ela
é chamada no máximo uma vez ao longo de muitos requests. Então:

    from ml.model_loader import load_yolo          # importe a função
    self._model = load_yolo(weights)               # chame UMA VEZ, depois faça cache

NÃO contorne esta função importando ``ultralytics.YOLO`` diretamente — a
verificação de load-once (e os testes do registry do nível 5) dependem desta costura.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_yolo(weights: str) -> Any:
    """Constrói e retorna um modelo YOLO do Ultralytics a partir de um caminho de pesos."""
    from ultralytics import YOLO

    return YOLO(weights)


def model_id_from_weights(weights: str) -> str:
    """Deriva um model id estável e legível a partir de um caminho de pesos.

    ex.: ``/path/yolov8n.pt`` -> ``yolov8n``;
         ``models/shapes-detector-v1.2.0.pt`` -> ``shapes-detector-v1.2.0``.
    """
    return Path(weights).stem
