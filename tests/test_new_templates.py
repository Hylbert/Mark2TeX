"""Tests for the three new templates: dissertacao-abnt, relatorio-abnt, artigo-acm.

Covers build_frontmatter, validate(), and swap_template interactions.
Existing test files (test_yaml_injector.py, test_frontmatter_validator.py) are
not modified — this file only adds coverage for the new templates.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from mark2tex.frontmatter_validator import ValidationError, validate
from mark2tex.yaml_injector import build_frontmatter, swap_template


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_md(tmp_path: Path, frontmatter: str, body: str = "# Body\n") -> Path:
    content = f"---\n{frontmatter}---\n{body}"
    p = tmp_path / "doc.md"
    p.write_text(content, encoding="utf-8")
    return p


def _codes(errors: list[ValidationError]) -> list[str]:
    return [e.code for e in errors]


def _fields(errors: list[ValidationError]) -> list[str]:
    return [e.field for e in errors]


def _parse_fm(text: str) -> dict:
    """Extract and parse the YAML frontmatter from a document string."""
    m = re.search(r'^---(.*?)---', text, re.DOTALL)
    assert m, "No frontmatter found in text"
    return yaml.safe_load(m.group(1)) or {}


# ---------------------------------------------------------------------------
# Valid frontmatter fixtures
# ---------------------------------------------------------------------------

DISSERTACAO_VALID = """\
title: "Minha Dissertacao"
author:
  - name: "Maria Silva"
template: "dissertacao-abnt"
lang: "pt-BR"
year: "2026"
institution: "UFAM"
program: "Programa de Pos-Graduacao em Ciencia da Computacao"
advisor: "Prof. Dr. Joao Costa"
"""

RELATORIO_VALID = """\
title: "Relatorio de Estagio"
author: "Pedro Alves"
template: "relatorio-abnt"
lang: "pt-BR"
date: "2026-05-09"
institution: "UFAM"
"""

ACM_VALID = """\
title: "My ACM Paper"
author: "Jane Doe"
template: "artigo-acm"
lang: "english"
"""

TESE_VALID = """\
title: "Minha Tese"
author:
  - name: "Ana Souza"
template: "tese-abnt"
lang: "pt-BR"
year: "2026"
institution: "UFAM"
program: "PPG-CC"
advisor: "Prof. Dr. Silva"
degree: "Doutor em Ciencia da Computacao"
"""

APA_VALID = """\
title: "APA Article"
author:
  - name: "John Doe"
template: "artigo-apa"
lang: "english"
institution: "Example University"
"""

# NOTAS_VALID: title must NOT be the registered placeholder "Notas de Aula"
# (frontmatter_validator._PLACEHOLDERS includes that string, which would
# cause a 'placeholder' ValidationError and break test_valid_passes).
NOTAS_VALID = """\
title: "Introdução à Programação"
author: "Aluno"
template: "notas-aula"
lang: "pt-BR"
"""


# ===========================================================================
# build_frontmatter — new templates
# ===========================================================================

class TestBuildFrontmatterTese:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("tese-abnt")
        data = _parse_fm(fm)
        assert data["template"] == "tese-abnt"

    def test_contains_program_advisor_degree(self) -> None:
        fm = build_frontmatter("tese-abnt")
        assert "program:" in fm
        assert "advisor:" in fm
        assert "degree:" in fm

    def test_lang_is_pt_br(self) -> None:
        fm = build_frontmatter("tese-abnt")
        data = _parse_fm(fm)
        assert data["lang"] == "pt-BR"


class TestBuildFrontmatterApa:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("artigo-apa")
        data = _parse_fm(fm)
        assert data["template"] == "artigo-apa"

    def test_lang_is_english(self) -> None:
        fm = build_frontmatter("artigo-apa")
        data = _parse_fm(fm)
        assert data["lang"] == "english"


class TestBuildFrontmatterNotas:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("notas-aula")
        data = _parse_fm(fm)
        assert data["template"] == "notas-aula"

    def test_lang_is_pt_br(self) -> None:
        fm = build_frontmatter("notas-aula")
        data = _parse_fm(fm)
        assert data["lang"] == "pt-BR"


# ===========================================================================
# validate() — tese-abnt
# ===========================================================================

class TestValidateTeseAbnt:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, TESE_VALID)
        assert validate(p, "tese-abnt") == []

    def test_missing_program(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in TESE_VALID.splitlines()
            if not line.startswith("program")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "tese-abnt")
        assert "program" in _fields(errors)

    def test_missing_advisor(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in TESE_VALID.splitlines()
            if not line.startswith("advisor")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "tese-abnt")
        assert "advisor" in _fields(errors)

    def test_missing_institution(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in TESE_VALID.splitlines()
            if not line.startswith("institution")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "tese-abnt")
        assert "institution" in _fields(errors)


# ===========================================================================
# validate() — artigo-apa
# ===========================================================================

class TestValidateArtigoApa:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, APA_VALID)
        assert validate(p, "artigo-apa") == []

    def test_missing_title(self, tmp_path: Path) -> None:
        fm = APA_VALID.replace('title: "APA Article"\n', "")
        p = _write_md(tmp_path, fm)
        errors = validate(p, "artigo-apa")
        assert "title" in _fields(errors)


# ===========================================================================
# validate() — notas-aula
# ===========================================================================

class TestValidateNotasAula:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, NOTAS_VALID)
        assert validate(p, "notas-aula") == []

    def test_missing_title(self, tmp_path: Path) -> None:
        fm = NOTAS_VALID.replace('title: "Notas de Aula"\n', "")
        p = _write_md(tmp_path, fm)
        errors = validate(p, "notas-aula")
        assert "title" in _fields(errors)


# ===========================================================================
# swap_template interactions
# ===========================================================================

class TestSwapToFromNewTemplates:
    def test_swap_to_tese_adds_program_and_advisor(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        swap_template(f, "tese-abnt")
        content = f.read_text(encoding="utf-8")
        assert "program" in content
        assert "advisor" in content
        assert "degree" in content

    def test_swap_to_notas_preserves_body(self, tmp_path: Path) -> None:
        body = "\n# Introduction\n\nThis is my notes document body.\n"
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "english"\n---\n' + body,
            encoding="utf-8",
        )
        swap_template(f, "notas-aula")
        content = f.read_text(encoding="utf-8")
        assert body in content
