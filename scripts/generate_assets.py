"""(Re)gera deterministicamente toda fixture de que este desafio precisa.

FORNECIDO — NÃO EDITAR. Rode via ``make assets`` (parte do ``make setup``).

Produz, a partir de uma seed fixa (para que as execuções sejam reproduzíveis):
  - data/images/sample.png        cena 640x480 (metadados do nível 1, smoke do nível 2)
  - data/video/sample.mp4         cenário 320x240 com marcador branco (nível 3)
  - data/datasets/shapes/         dataset sintético em formato YOLO (nível 4)

Notas de design
---------------
* O marcador do nível 3 é BRANCO sobre PRETO: dominado pela luma, então ele
  sobrevive intacto à compressão mp4 (sem surpresas de chroma-subsampling). Depois
  de escrever o vídeo, nós o relemos e verificamos que o marcador cai dentro/fora
  da zona exatamente nos frames pretendidos — uma falha barulhenta NO SETUP é melhor
  que um teste instável. (Essa verificação a nível de frame deliberadamente NÃO
  computa eventos/debounce — esse é o seu trabalho do nível 3.)
* O dataset de shapes é desenhado a partir de um RNG fixo; train e val usam streams
  de RNG disjuntos, então não há vazamento por construção.
"""

from __future__ import annotations

import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

from app import config

SEED = 0

# --- Cenário entregue do nível 3 ---------------------------------------------
VIDEO_SIZE = (320, 240)  # (w, h)
VIDEO_FPS = 10
VIDEO_FRAMES = 120
MARKER_RGB = (255, 255, 255)
BG_RGB = (0, 0, 0)
MARKER_SIZE = 40
ZONE = (110, 70, 210, 170)  # x1, y1, x2, y2 (pixels)
ZONE_CENTER = ((ZONE[0] + ZONE[2]) // 2, (ZONE[1] + ZONE[3]) // 2)
OUT_POS = (30, 30)  # centro do marcador bem fora da zona


def in_zone_shipped(frame_idx: int) -> bool:
    """Frames RAW onde o marcador fica dentro da zona (o cenário do nível 3).

    Duas intrusões sustentadas (uma longa, e uma que vai até o fim do vídeo para
    exercitar o flush de fim-de-vídeo) mais um blip de um único frame em 80 que
    deve ser suprimido pelo debouncing.
    """
    return (20 <= frame_idx <= 60) or (frame_idx == 80) or (92 <= frame_idx <= 116)


# --------------------------------------------------------------------------- #
# Nível 3 — vídeo
# --------------------------------------------------------------------------- #
def _marker_frame(center: tuple[int, int]) -> np.ndarray:
    w, h = VIDEO_SIZE
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = BG_RGB[::-1]  # BGR
    half = MARKER_SIZE // 2
    cx, cy = center
    x1, y1 = max(0, cx - half), max(0, cy - half)
    x2, y2 = min(w, cx + half), min(h, cy + half)
    frame[y1:y2, x1:x2] = MARKER_RGB[::-1]  # BGR (branco é simétrico de qualquer forma)
    return frame


def write_scenario_video(path, size, fps, n_frames, in_zone_fn) -> None:
    w, h = size
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"cv2 não conseguiu abrir um writer mp4v para {path}")
    for f in range(n_frames):
        center = ZONE_CENTER if in_zone_fn(f) else OUT_POS
        writer.write(_marker_frame(center))
    writer.release()


def validate_scenario_video(path, n_frames, in_zone_fn) -> None:
    """Relê o vídeo e verifica que o marcador está dentro/fora da zona exatamente
    nos frames RAW pretendidos (apenas a nível de frame — sem lógica de evento)."""
    from ml.detectors import SimpleColorDetector

    detector = SimpleColorDetector(target_rgb=MARKER_RGB, tol=70, min_area=150)
    cap = cv2.VideoCapture(str(path))
    zx1, zy1, zx2, zy2 = ZONE
    idx = 0
    mismatches: list[int] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        dets = detector.detect(frame)
        in_zone = False
        for d in dets:
            cx = (d.box[0] + d.box[2]) / 2
            cy = (d.box[1] + d.box[3]) / 2
            if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                in_zone = True
                break
        if in_zone != in_zone_fn(idx):
            mismatches.append(idx)
        idx += 1
    cap.release()
    if idx != n_frames:
        raise RuntimeError(f"o vídeo tem {idx} frames, esperava {n_frames}")
    if mismatches:
        raise RuntimeError(
            f"auto-verificação do vídeo falhou em {len(mismatches)} frame(s): {mismatches[:10]}… "
            f"(drift de cor do marcador/codec — ajuste o tol do detector ou o marcador)"
        )


# --------------------------------------------------------------------------- #
# Nível 2 / Nível 1 — imagem de amostra
# --------------------------------------------------------------------------- #
def gen_sample_image(path, size=(640, 480)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, (40, 44, 52))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 80, 240, 300], fill=(200, 80, 60))
    d.ellipse([320, 120, 520, 320], fill=(70, 160, 210))
    d.polygon([(420, 360), (360, 460), (480, 460)], fill=(120, 200, 120))
    img.save(path, format="PNG")


# --------------------------------------------------------------------------- #
# Nível 4 — dataset sintético de shapes (formato YOLO)
# --------------------------------------------------------------------------- #
SHAPE_CLASSES = ["circle", "square", "triangle"]


def _draw_shapes(rng: random.Random, size: int):
    img = Image.new("RGB", (size, size), (20, 20, 28))
    d = ImageDraw.Draw(img)
    labels: list[tuple[int, float, float, float, float]] = []
    for _ in range(rng.randint(1, 3)):
        cls = rng.randint(0, 2)
        side = rng.randint(size // 8, size // 4)
        x = rng.randint(0, size - side)
        y = rng.randint(0, size - side)
        color = (rng.randint(120, 255), rng.randint(120, 255), rng.randint(120, 255))
        if cls == 0:
            d.ellipse([x, y, x + side, y + side], fill=color)
        elif cls == 1:
            d.rectangle([x, y, x + side, y + side], fill=color)
        else:
            d.polygon([(x + side // 2, y), (x, y + side), (x + side, y + side)], fill=color)
        cx, cy = (x + side / 2) / size, (y + side / 2) / size
        w = h = side / size
        labels.append((cls, cx, cy, w, h))
    return img, labels


def gen_shapes_dataset(root, n_train=200, n_val=80, size=384) -> None:
    for split, n, seed in (("train", n_train, SEED), ("val", n_val, SEED + 1000)):
        img_dir = root / "images" / split
        lbl_dir = root / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        rng = random.Random(seed)
        for i in range(n):
            img, labels = _draw_shapes(rng, size)
            img.save(img_dir / f"{split}_{i:04d}.png", format="PNG")
            lines = [f"{c} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}" for c, cx, cy, w, h in labels]
            (lbl_dir / f"{split}_{i:04d}.txt").write_text("\n".join(lines) + "\n")
    yaml_text = (
        f"path: {root.resolve()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "names:\n" + "".join(f"  {i}: {n}\n" for i, n in enumerate(SHAPE_CLASSES))
    )
    (root / "data.yaml").write_text(yaml_text)


def main() -> int:
    print("Gerando fixtures (seed=%d)…" % SEED)
    gen_sample_image(config.SAMPLE_IMAGE)
    print(f"✓ {config.SAMPLE_IMAGE.relative_to(config.ROOT)}")

    write_scenario_video(config.SAMPLE_VIDEO, VIDEO_SIZE, VIDEO_FPS, VIDEO_FRAMES, in_zone_shipped)
    validate_scenario_video(config.SAMPLE_VIDEO, VIDEO_FRAMES, in_zone_shipped)
    print(f"✓ {config.SAMPLE_VIDEO.relative_to(config.ROOT)} (validado)")

    gen_shapes_dataset(config.SHAPES_DATASET)
    print(f"✓ {config.SHAPES_DATASET.relative_to(config.ROOT)} (200 train / 80 val)")
    print("✓ assets prontos\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
