"""Verifica que os arquivos protegidos (não-editar) estão intactos.

Esses arquivos são o contrato + a maquinaria dos avaliadores. Você implementa os STUBS
(``app/levels/level1-3.py``, ``ml/train.py``, ``ml/evaluate.py``,
``ml/registry.py``) e pode adicionar seus próprios arquivos/testes — mas editar um
arquivo protegido é sinalizado. Se você acredita que um arquivo protegido tem um bug,
NÃO o edite: anote em ``NOTES.md`` e descreva a correção.

Uso:
    python scripts/check_integrity.py            # verifica contra o manifesto
    python scripts/check_integrity.py --write     # (mantenedores) regenera o manifesto
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "PROTECTED.sha256"

# Arquivos que o candidato não deve modificar. Globs são resolvidos relativos a ROOT.
PROTECTED_GLOBS = [
    "app/main.py",
    "app/config.py",
    "app/schemas.py",
    "app/levels/level4.py",
    "app/levels/level5.py",
    "ml/model_loader.py",
    "ml/detectors.py",
    "ml/versioning.py",
    "tests/conftest.py",
    "tests/acceptance/*.py",
    "scripts/preflight.py",
    "scripts/generate_assets.py",
    "scripts/fetch_weights.py",
    "scripts/check_commits.py",
    "scripts/check_integrity.py",
]


def protected_files() -> list[Path]:
    seen: set[Path] = set()
    for pattern in PROTECTED_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            if p.is_file():
                seen.add(p)
    return sorted(seen)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_manifest() -> None:
    lines = [f"{sha256(p)}  {p.relative_to(ROOT).as_posix()}" for p in protected_files()]
    MANIFEST.write_text("\n".join(lines) + "\n")
    print(f"Escrevi {len(lines)} hashes em {MANIFEST.relative_to(ROOT)}")


def verify() -> int:
    if not MANIFEST.exists():
        print("⚠ nenhum manifesto encontrado — rode com --write (mantenedores). Pulando.")
        return 0
    expected: dict[str, str] = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip():
            digest, rel = line.split("  ", 1)
            expected[rel] = digest

    problems: list[str] = []
    for rel, digest in expected.items():
        p = ROOT / rel
        if not p.exists():
            problems.append(f"  AUSENTE   {rel}")
        elif sha256(p) != digest:
            problems.append(f"  MODIFICADO {rel}")

    if problems:
        print("❌ arquivos protegidos foram alterados (não edite estes):")
        print("\n".join(problems))
        print("\nSe você acha que algum tem um bug, reverta-o e anote o problema em NOTES.md.")
        return 1
    print(f"✓ todos os {len(expected)} arquivos protegidos estão intactos.")
    return 0


def main() -> int:
    if "--write" in sys.argv:
        write_manifest()
        return 0
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
