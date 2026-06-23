"""Gramática canônica de versionamento de modelos, compartilhada pelos níveis 4 e 5.

FORNECIDO — NÃO EDITE (arquivo protegido, veja scripts/check_integrity.py).

O NOME DO ARQUIVO do artefato é a fonte autoritativa da versão de um modelo. Use
estes helpers no nível 4 (quando você salva) e no nível 5 (quando você descobre),
para que as duas metades concordem. Apenas SemVer core — ``MAJOR.MINOR.PATCH`` (sem
metadados de pre-release/build, cujos pontos/sinais de mais colidiriam com o parsing
de ``.pt``).

    model_filename("shapes-detector", "1.2.0")  -> "shapes-detector-v1.2.0.pt"
    parse_model_filename("shapes-detector-v1.2.0.pt") -> ("shapes-detector", "1.2.0")
"""

from __future__ import annotations

import re
from pathlib import Path

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
MODEL_FILENAME_RE = re.compile(r"^(?P<name>[A-Za-z0-9_-]+)-v(?P<version>\d+\.\d+\.\d+)\.pt$")


def is_semver(version: str) -> bool:
    """True se e somente se ``version`` for uma string SemVer core ``MAJOR.MINOR.PATCH``."""
    return bool(SEMVER_RE.match(version))


def model_filename(name: str, version: str) -> str:
    """Monta o nome de arquivo canônico do artefato para ``name`` na ``version``."""
    if not is_semver(version):
        raise ValueError(f"versão não é SemVer core: {version!r}")
    return f"{name}-v{version}.pt"


def parse_model_filename(path: str | Path) -> tuple[str, str] | None:
    """Retorna ``(name, version)`` para um artefato versionado, ou None se ele não
    casar com a gramática canônica."""
    m = MODEL_FILENAME_RE.match(Path(path).name)
    if not m:
        return None
    return m.group("name"), m.group("version")


def bump(version: str, kind: str) -> str:
    """Retorna ``version`` incrementada por ``kind`` em {'major','minor','patch'}.

    Regras SemVer para um modelo detector:
      - major: mudança incompatível no conjunto de classes ou no contrato de I/O;
      - minor: mesmas classes/contrato, novo treino ou dados adicionados;
      - patch: retreino de correção, sem mudança de comportamento.
    """
    if not is_semver(version):
        raise ValueError(f"versão não é SemVer core: {version!r}")
    major, minor, patch = (int(x) for x in version.split("."))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"tipo de bump desconhecido: {kind!r}")
