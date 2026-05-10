"""Tests for the three new templates: dissertacao-abnt, relatorio-abnt, artigo-acm.

Covers build_frontmatter, validate(), and swap_template interactions.
Existing test files (test_yaml_injector.py, test_frontmatter_validator.py) are
not modified — this file only adds coverage for the new templates.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

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


# ===========================================================================
# build_frontmatter
# ===========================================================================

class TestBuildFrontmatterDissertacao:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("dissertacao-abnt")
        assert 'template: "dissertacao-abnt"' in fm

    def test_contains_program_field(self) -> None:
        fm = build_frontmatter("dissertacao-abnt")
        assert "program:" in fm

    def test_contains_advisor_field(self) -> None:
        fm = build_frontmatter("dissertacao-abnt")
        assert "advisor:" in fm

    def test_contains_degree_field(self) -> None:
        fm = build_frontmatter("dissertacao-abnt")
        assert "degree:" in fm

    def test_starts_and_ends_with_dashes(self) -> None:
        lines = build_frontmatter("dissertacao-abnt").strip().splitlines()
        assert lines[0] == "---"
        assert lines[-1] == "---"

    def test_lang_is_pt_br(self) -> None:
        fm = build_frontmatter("dissertacao-abnt")
        assert 'lang: "pt-BR"' in fm


class TestBuildFrontmatterRelatorio:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("relatorio-abnt")
        assert 'template: "relatorio-abnt"' in fm

    def test_contains_report_type_field(self) -> None:
        fm = build_frontmatter("relatorio-abnt")
        assert "report-type:" in fm

    def test_contains_institution_field(self) -> None:
        fm = build_frontmatter("relatorio-abnt")
        assert "institution:" in fm

    def test_lang_is_pt_br(self) -> None:
        fm = build_frontmatter("relatorio-abnt")
        assert 'lang: "pt-BR"' in fm


class TestBuildFrontmatterACM:
    def test_contains_template_key(self) -> None:
        fm = build_frontmatter("artigo-acm")
        assert 'template: "artigo-acm"' in fm

    def test_lang_is_english(self) -> None:
        # acmart uses babel internally; 'english' is the correct default
        fm = build_frontmatter("artigo-acm")
        assert 'lang: "english"' in fm

    def test_starts_and_ends_with_dashes(self) -> None:
        lines = build_frontmatter("artigo-acm").strip().splitlines()
        assert lines[0] == "---"
        assert lines[-1] == "---"


# ===========================================================================
# validate() — dissertacao-abnt
# ===========================================================================

class TestValidateDissertacaoAbnt:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, DISSERTACAO_VALID)
        assert validate(p, "dissertacao-abnt") == []

    def test_missing_year(self, tmp_path: Path) -> None:
        fm = DISSERTACAO_VALID.replace('year: "2026"\n', "")
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert "year" in _fields(errors)
        assert "missing" in _codes(errors)

    def test_missing_program(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in DISSERTACAO_VALID.splitlines()
            if not line.startswith("program")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert "program" in _fields(errors)

    def test_missing_advisor(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in DISSERTACAO_VALID.splitlines()
            if not line.startswith("advisor")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert "advisor" in _fields(errors)

    def test_missing_institution(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in DISSERTACAO_VALID.splitlines()
            if not line.startswith("institution")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert "institution" in _fields(errors)

    def test_placeholder_title_detected(self, tmp_path: Path) -> None:
        fm = DISSERTACAO_VALID.replace('title: "Minha Dissertacao"', 'title: "T\u00edtulo da Disserta\u00e7\u00e3o"')
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert any(e.code == "placeholder" and e.field == "title" for e in errors)

    def test_placeholder_program_detected(self, tmp_path: Path) -> None:
        fm = DISSERTACAO_VALID.replace(
            'program: "Programa de Pos-Graduacao em Ciencia da Computacao"',
            'program: "Programa de P\u00f3s-Gradua\u00e7\u00e3o em Nome da \u00c1rea"',
        )
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert any(e.code == "placeholder" and e.field == "program" for e in errors)

    def test_placeholder_advisor_detected(self, tmp_path: Path) -> None:
        fm = DISSERTACAO_VALID.replace(
            'advisor: "Prof. Dr. Joao Costa"',
            'advisor: "Prof. Dr. Nome do Orientador"',
        )
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert any(e.code == "placeholder" and e.field == "advisor" for e in errors)

    def test_template_mismatch_detected(self, tmp_path: Path) -> None:
        fm = DISSERTACAO_VALID.replace('template: "dissertacao-abnt"', 'template: "tcc-abnt"')
        p = _write_md(tmp_path, fm)
        errors = validate(p, "dissertacao-abnt")
        assert any(e.code == "template_mismatch" for e in errors)


# ===========================================================================
# validate() — relatorio-abnt
# ===========================================================================

class TestValidateRelatorioAbnt:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, RELATORIO_VALID)
        assert validate(p, "relatorio-abnt") == []

    def test_missing_institution(self, tmp_path: Path) -> None:
        fm = "\n".join(
            line for line in RELATORIO_VALID.splitlines()
            if not line.startswith("institution")
        ) + "\n"
        p = _write_md(tmp_path, fm)
        errors = validate(p, "relatorio-abnt")
        assert "institution" in _fields(errors)

    def test_placeholder_title_detected(self, tmp_path: Path) -> None:
        fm = RELATORIO_VALID.replace('title: "Relatorio de Estagio"', 'title: "T\u00edtulo do Relat\u00f3rio"')
        p = _write_md(tmp_path, fm)
        errors = validate(p, "relatorio-abnt")
        assert any(e.code == "placeholder" and e.field == "title" for e in errors)

    def test_does_not_require_advisor(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, RELATORIO_VALID)
        errors = validate(p, "relatorio-abnt")
        assert "advisor" not in _fields(errors)

    def test_does_not_require_year(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, RELATORIO_VALID)
        errors = validate(p, "relatorio-abnt")
        assert "year" not in _fields(errors)


# ===========================================================================
# validate() — artigo-acm
# ===========================================================================

class TestValidateArtigoAcm:
    def test_valid_passes(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, ACM_VALID)
        assert validate(p, "artigo-acm") == []

    def test_does_not_require_institution(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, ACM_VALID)
        errors = validate(p, "artigo-acm")
        assert "institution" not in _fields(errors)

    def test_does_not_require_year(self, tmp_path: Path) -> None:
        p = _write_md(tmp_path, ACM_VALID)
        errors = validate(p, "artigo-acm")
        assert "year" not in _fields(errors)

    def test_missing_title(self, tmp_path: Path) -> None:
        fm = ACM_VALID.replace('title: "My ACM Paper"\n', "")
        p = _write_md(tmp_path, fm)
        errors = validate(p, "artigo-acm")
        assert "title" in _fields(errors)

    def test_placeholder_title_detected(self, tmp_path: Path) -> None:
        fm = ACM_VALID.replace('title: "My ACM Paper"', 'title: "Article Title"')
        p = _write_md(tmp_path, fm)
        errors = validate(p, "artigo-acm")
        assert any(e.code == "placeholder" and e.field == "title" for e in errors)

    def test_placeholder_author_detected(self, tmp_path: Path) -> None:
        fm = ACM_VALID.replace('author: "Jane Doe"', 'author: "Author"')
        p = _write_md(tmp_path, fm)
        errors = validate(p, "artigo-acm")
        assert any(e.code == "placeholder" and e.field == "author" for e in errors)


# ===========================================================================
# swap_template interactions
# ===========================================================================

class TestSwapToFromNewTemplates:
    def test_swap_to_dissertacao_adds_program_and_advisor(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        swap_template(f, "dissertacao-abnt")
        content = f.read_text(encoding="utf-8")
        assert "program" in content
        assert "advisor" in content
        assert "year" in content

    def test_swap_from_dissertacao_removes_exclusive_fields(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "dissertacao-abnt"\nlang: "pt-BR"\nyear: "2026"\n'
            'institution: "UFAM"\nprogram: "PPG-CC"\nadvisor: "Prof. X"\n'
            'degree: "Mestre"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        swap_template(f, "artigo-ieee")
        content = f.read_text(encoding="utf-8")
        assert "program" not in content
        assert "advisor" not in content
        assert "degree" not in content
        assert "year" not in content

    def test_swap_to_relatorio_adds_report_type(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        swap_template(f, "relatorio-abnt")
        content = f.read_text(encoding="utf-8")
        assert "report-type" in content
        assert "institution" in content

    def test_swap_preserves_title_when_switching_to_acm(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "My Real Title"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "english"\n---\n\n# Body\n',
            encoding="utf-8",
        )
        swap_template(f, "artigo-acm")
        content = f.read_text(encoding="utf-8")
        assert 'title: "My Real Title"' in content
        assert 'template: "artigo-acm"' in content

    def test_swap_body_preserved_for_new_templates(self, tmp_path: Path) -> None:
        body = "\n# Introduction\n\nThis is my document body.\n"
        f = tmp_path / "doc.md"
        f.write_text(
            '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
            'template: "artigo-ieee"\nlang: "english"\n---\n' + body,
            encoding="utf-8",
        )
        swap_template(f, "artigo-acm")
        content = f.read_text(encoding="utf-8")
        assert body in content
