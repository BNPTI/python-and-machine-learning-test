#!/usr/bin/env python3
"""Runner cross-platform do desafio — Windows, macOS e Linux.

Faz o mesmo que o Makefile, mas depende apenas de Python, então funciona igual em
qualquer sistema operacional. Rode com o seu Python 3.11 ou 3.12:

    python dev.py setup       # cria a venv, instala deps, baixa pesos, gera assets
    python dev.py test        # roda toda a suíte de aceitação (inclui treino lento)
    python dev.py test-fast   # tudo exceto os testes lentos de torch/treino
    python dev.py run         # sobe a API em http://127.0.0.1:8000/docs
    python dev.py lint        # ruff
    python dev.py check       # integridade dos arquivos protegidos + lint de commits
    python dev.py clean       # remove venv, caches e artefatos gerados

No Windows use o launcher do Python, ex.: ``py -3.12 dev.py setup``.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
IS_WIN = os.name == "nt"
VENV_BIN = VENV / ("Scripts" if IS_WIN else "bin")
VENV_PY = VENV_BIN / ("python.exe" if IS_WIN else "python")

MIN_PY = (3, 11)
MAX_PY = (3, 12)


def _env() -> dict:
    """Ambiente para os subprocessos: Ultralytics local + raiz no PYTHONPATH."""
    env = os.environ.copy()
    env["YOLO_CONFIG_DIR"] = str(ROOT / ".ultralytics")
    env["MPLBACKEND"] = "Agg"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + existing if existing else "")
    return env


def run(cmd: list, check: bool = True) -> int:
    printable = " ".join(str(c) for c in cmd)
    print(f"> {printable}", flush=True)
    return subprocess.run([str(c) for c in cmd], cwd=ROOT, env=_env(), check=check).returncode


def require_venv() -> None:
    if not VENV_PY.exists():
        sys.exit("venv não encontrada. Rode primeiro: python dev.py setup")


def ensure_venv() -> None:
    if VENV_PY.exists():
        return
    major, minor = sys.version_info[:2]
    if not (MIN_PY <= (major, minor) <= MAX_PY):
        sys.exit(
            f"Python {major}.{minor} detectado, mas o desafio exige Python 3.11 ou 3.12 "
            f"(torch/ultralytics não publicam wheels fora dessa faixa).\n"
            f"Rode este script com o interpretador certo — ex.: 'py -3.12 dev.py setup' "
            f"(Windows) ou 'python3.12 dev.py setup' (macOS/Linux)."
        )
    print(f"Criando venv em {VENV} com {sys.executable} …")
    run([sys.executable, "-m", "venv", str(VENV)])


def cmd_setup(_args) -> None:
    run([sys.executable, "scripts/preflight.py"])
    ensure_venv()
    run([VENV_PY, "-m", "pip", "install", "--upgrade", "pip"])
    run([VENV_PY, "-m", "pip", "install", "-r", "requirements.txt"])
    # Desliga sync/telemetria do Ultralytics (best-effort).
    run(
        [VENV_PY, "-c", "from ultralytics import settings; settings.update({'sync': False})"],
        check=False,
    )
    run([VENV_PY, "scripts/fetch_weights.py"])
    run([VENV_PY, "scripts/generate_assets.py"])
    print("\n✅ Setup concluído. Próximo passo: python dev.py test")


def cmd_test(_args) -> None:
    require_venv()
    run([VENV_PY, "-m", "pytest"])


def cmd_test_fast(_args) -> None:
    require_venv()
    run([VENV_PY, "-m", "pytest", "-m", "not slow"])


def cmd_run(_args) -> None:
    require_venv()
    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = os.environ.get("APP_PORT", "8000")
    run([VENV_PY, "-m", "uvicorn", "app.main:app", "--reload", "--host", host, "--port", port])


def cmd_lint(_args) -> None:
    require_venv()
    run([VENV_PY, "-m", "ruff", "check", "."])


def cmd_assets(_args) -> None:
    require_venv()
    run([VENV_PY, "scripts/generate_assets.py"])


def cmd_fetch_weights(_args) -> None:
    require_venv()
    run([VENV_PY, "scripts/fetch_weights.py"])


def cmd_check_integrity(_args) -> None:
    require_venv()
    run([VENV_PY, "scripts/check_integrity.py"])


def cmd_check_commits(_args) -> None:
    require_venv()
    run([VENV_PY, "scripts/check_commits.py"])


def cmd_check(_args) -> None:
    cmd_check_integrity(_args)
    cmd_check_commits(_args)


def cmd_clean(_args) -> None:
    caches = (".pytest_cache", ".ruff_cache", ".ultralytics", "runs")
    for p in (VENV, *(ROOT / c for c in caches)):
        shutil.rmtree(p, ignore_errors=True)
    for pt in (ROOT / "models").glob("*.pt"):
        pt.unlink()
    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    print("Limpo.")


COMMANDS = {
    "setup": cmd_setup,
    "test": cmd_test,
    "test-fast": cmd_test_fast,
    "run": cmd_run,
    "lint": cmd_lint,
    "assets": cmd_assets,
    "fetch-weights": cmd_fetch_weights,
    "check": cmd_check,
    "check-integrity": cmd_check_integrity,
    "check-commits": cmd_check_commits,
    "clean": cmd_clean,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runner cross-platform do desafio (Windows/macOS/Linux).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Comandos: " + ", ".join(COMMANDS),
    )
    parser.add_argument("command", choices=COMMANDS, help="o que executar")
    args = parser.parse_args()
    try:
        COMMANDS[args.command](args)
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
