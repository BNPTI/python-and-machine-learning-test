"""Um detector determinístico e leve em dependências, usado pelo nível 3.

FORNECIDO — NÃO EDITE (arquivo protegido, veja scripts/check_integrity.py).

``SimpleColorDetector`` encontra marcadores de cor sólida em um frame e os retorna
como objetos ``Detection`` — o mesmo formato que o seu detector YOLO do nível 2
retorna. É isso que o teste de aceitação do nível 3 injeta, para que a lógica de anomalia
temporal que você escrever seja testada de forma **determinística**, independente
de qualquer rede neural.

Em produção, você injetaria aqui o seu ``Detector`` YOLO do nível 2; o contrato
de ``analyze_video`` é agnóstico ao detector de propósito (ele só precisa de um
objeto com ``.detect(frame_bgr) -> list[Detection]``).
"""

from __future__ import annotations

import cv2
import numpy as np

from app.schemas import Detection


class SimpleColorDetector:
    """Detecta regiões conectadas cuja cor é próxima de ``target_rgb``.

    Parâmetros
    ----------
    target_rgb : tuple[int, int, int]
        Cor a procurar, em RGB (0-255).
    label : str
        Rótulo atribuído a toda detecção que ele retorna.
    tol : int
        Tolerância absoluta por canal para o casamento de cor.
    min_area : int
        Área mínima do blob (em pixels) para contar como uma detecção.
    """

    def __init__(
        self,
        target_rgb: tuple[int, int, int],
        label: str = "marker",
        tol: int = 45,
        min_area: int = 80,
    ) -> None:
        self.target_rgb = np.array(target_rgb, dtype=np.int16)
        self.label = label
        self.tol = int(tol)
        self.min_area = int(min_area)

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        """Retorna detecções para um frame BGR (como produzido pelo cv2)."""
        rgb = frame_bgr[:, :, ::-1].astype(np.int16)
        diff = np.abs(rgb - self.target_rgb)
        mask = np.all(diff <= self.tol, axis=2).astype(np.uint8)

        num, _labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
        out: list[Detection] = []
        for i in range(1, num):  # pula o fundo (background, 0)
            x, y, w, h, area = stats[i]
            if area < self.min_area:
                continue
            out.append(
                Detection(
                    label=self.label,
                    confidence=1.0,
                    box=[float(x), float(y), float(x + w), float(y + h)],
                )
            )
        out.sort(key=lambda d: d.box[0])
        return out
