"""Valida Conventional Commits (informativo).

Esperamos uma série pequena e lógica de commits — pelo menos um por nível que você
tentar — usando Conventional Commits, por exemplo:

    feat(level1): implement health and image metadata endpoints
    feat(level2): add YOLO object-detection endpoint
    fix(level3): flush an open event at end of video

Isto é INFORMATIVO: reporta problemas e sai com 0 a menos que você passe ``--strict``.
A higiene dos commits não é auto-bloqueada.
"""

from __future__ import annotations

import re
import subprocess
import sys

TYPES = "feat|fix|refactor|docs|perf|test|chore|build|ci|style|revert"
SUBJECT_RE = re.compile(rf"^(?:{TYPES})(?:\([a-z0-9._-]+\))?!?: .+")


def commits() -> list[tuple[str, str]]:
    try:
        out = subprocess.run(
            ["git", "log", "--no-merges", "--format=%h%x1f%s", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ não é um repositório git (ou git indisponível) — pulando.")
        return []
    rows = []
    for line in out.splitlines():
        if "\x1f" in line:
            h, subject = line.split("\x1f", 1)
            rows.append((h, subject))
    return rows


def main() -> int:
    strict = "--strict" in sys.argv
    rows = commits()
    if not rows:
        return 0

    bad = [(h, s) for h, s in rows if not SUBJECT_RE.match(s)]
    scopes = sorted({m.group(1) for _, s in rows if (m := re.search(r"\(level([1-5])\)", s))})

    print(f"Analisados {len(rows)} commit(s).")
    print(f"Níveis referenciados por escopo: {', '.join('L' + s for s in scopes) or 'nenhum'}")
    if bad:
        print(f"\n⚠ {len(bad)} commit(s) NÃO seguem Conventional Commits:")
        for h, s in bad:
            print(f"  {h}  {s}")
        print('\n  Formato: "type(scope): summary"  ex.  feat(level2): add /detect')
        if strict:
            return 1
    else:
        print("✓ todos os commits seguem Conventional Commits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
