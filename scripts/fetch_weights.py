"""Garante que os pesos pré-treinados yolov8n.pt estão presentes (e reporta seu hash).

Os pesos nunca são commitados (tamanho + AGPL da Ultralytics — veja o NOTICE). Este
script os disponibiliza localmente e imprime o sha256 para que os mantenedores possam
fixá-lo (pin).

Defina ``FG_WEIGHTS_SHA256`` (env) para impor um checksum exato; caso contrário a
verificação é apenas informativa e somente imprime o digest.
"""

from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "yolov8n.pt"
FALLBACK_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_weights() -> Path:
    if TARGET.exists() and TARGET.stat().st_size > 0:
        return TARGET
    # Prefere o resolver da própria Ultralytics (lida com o asset release atual).
    try:
        from ultralytics import YOLO

        YOLO("yolov8n.pt")  # baixa para o CWD se ausente
        if TARGET.exists():
            return TARGET
        # A Ultralytics pode colocá-lo em outro lugar; encontra e linka para ROOT.
        for cand in (Path.cwd() / "yolov8n.pt",):
            if cand.exists():
                return cand
    except Exception as exc:  # noqa: BLE001 — cai no fallback de download direto
        print(f"  (caminho de download da ultralytics indisponível: {exc}; tentando URL direta)")
    print(f"Baixando {FALLBACK_URL} …")
    urllib.request.urlretrieve(FALLBACK_URL, TARGET)  # noqa: S310
    return TARGET


def main() -> int:
    path = ensure_weights()
    digest = sha256(path)
    print(f"✓ weights: {path}  ({path.stat().st_size / 1e6:.1f} MB)")
    print(f"  sha256: {digest}")

    expected = os.environ.get("FG_WEIGHTS_SHA256")
    if expected:
        if digest != expected:
            print(f"❌ checksum não confere! esperava {expected}", file=sys.stderr)
            return 1
        print("✓ checksum confere com FG_WEIGHTS_SHA256")
    else:
        print("  (informativo — defina FG_WEIGHTS_SHA256 para fixar este valor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
