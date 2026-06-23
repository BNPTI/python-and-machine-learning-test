"""Falha rápido com uma mensagem acionável se o ambiente não puder rodar este teste.

Executado por ``make setup`` (e seguro para rodar diretamente) ANTES de qualquer
instalação de dependência, porque torch/ultralytics só fornecem wheels para
Python 3.11 e 3.12.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

MIN = (3, 11)
MAX_EXCLUSIVE = (3, 13)
MIN_FREE_GB = 5.0


def _fail(msg: str) -> None:
    print(f"\n❌ preflight: {msg}\n", file=sys.stderr)
    sys.exit(1)


def check_python() -> None:
    v = sys.version_info
    if not (MIN <= (v.major, v.minor) < MAX_EXCLUSIVE):
        _fail(
            f"Python {v.major}.{v.minor} detectado, mas este desafio precisa de "
            f"Python 3.11 ou 3.12 (torch/ultralytics não têm wheels fora dessa "
            f"faixa; o pip tentaria compilar a partir do código-fonte e falharia).\n"
            f"   Corrija, por exemplo:\n"
            f"     pyenv install 3.12.7 && pyenv local 3.12.7\n"
            f"     # ou:  uv venv --python 3.12\n"
            f"   depois rode novamente:  make setup PYTHON=python3.12"
        )
    print(f"✓ Python {v.major}.{v.minor}.{v.micro}")


def check_disk() -> None:
    free_gb = shutil.disk_usage(Path.cwd()).free / 1e9
    if free_gb < MIN_FREE_GB:
        _fail(
            f"apenas {free_gb:.1f} GB livres; a instalação do torch/ultralytics "
            f"mais os pesos do modelo precisam de ~{MIN_FREE_GB:.0f} GB. Libere espaço e tente de novo."
        )
    print(f"✓ Disco livre: {free_gb:.1f} GB")


def main() -> None:
    print("Rodando verificações de preflight…")
    check_python()
    check_disk()
    print("✓ preflight OK\n")


if __name__ == "__main__":
    main()
