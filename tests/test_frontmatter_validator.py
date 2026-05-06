"""Tests for mark2tex.frontmatter_validator."""
from __future__ import annotations

from pathlib import Path

from mark2tex.frontmatter_validator import ValidationError, validate

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
# Happy paths
# ---------------------------------------------------------------------------

TCC_VALID = """\
title: "Meu TCC"
author:
  - name: "Maria Silva"
template: "tcc-abnt"
lang: "pt-BR"
year: "2026"
institution: "UFAM"
course: "Ciencia da Computacao"
advisor: "Prof. Dr. Joao Costa"
"""

IEEE_VALID = """\
title: "My Paper"
author: "John Doe"
template: "artigo-ieee"
lang: "en-US"
"""


def test_valid_tcc_abnt(tmp_path: Path) -> None:
    p = _write_md(tmp_path, TCC_VALID)
    assert validate(p, "tcc-abnt") == []


def test_valid_artigo_ieee(tmp_path: Path) -> None:
    p = _write_md(tmp_path, IEEE_VALID)
    assert validate(p, "artigo-ieee") == []


# ---------------------------------------------------------------------------
# parse errors
# ---------------------------------------------------------------------------

def test_no_frontmatter_returns_parse_error(tmp_path: Path) -> None:
    p = tmp_path / "doc.md"
    p.write_text("# Just a heading\n", encoding="utf-8")
    errors = validate(p, "tcc-abnt")
    assert _codes(errors) == ["parse_error"]


def test_unreadable_file_returns_parse_error(tmp_path: Path) -> None:
    p = tmp_path / "missing.md"
    errors = validate(p, "tcc-abnt")
    assert _codes(errors) == ["parse_error"]


def test_empty_frontmatter_block_returns_parse_error(tmp_path: Path) -> None:
    p = tmp_path / "doc.md"
    p.write_text("---\n---\n# Body\n", encoding="utf-8")
    errors = validate(p, "tcc-abnt")
    assert _codes(errors) == ["parse_error"]


def test_malformed_yaml_returns_parse_error_no_raise(tmp_path: Path) -> None:
    p = tmp_path / "doc.md"
    p.write_text("---\n: bad: yaml: [\n---\n# Body\n", encoding="utf-8")
    errors = validate(p, "tcc-abnt")
    assert len(errors) == 1
    assert errors[0].code == "parse_error"


# ---------------------------------------------------------------------------
# Missing fields
# ---------------------------------------------------------------------------

def test_missing_title(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('title: "Meu TCC"\n', "")
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert "missing" in _codes(errors)
    assert "title" in _fields(errors)


def test_missing_author(tmp_path: Path) -> None:
    lines = [
        line for line in TCC_VALID.splitlines()
        if not line.startswith("author") and not line.strip().startswith("- name")
    ]
    fm = "\n".join(lines) + "\n"
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert "missing" in _codes(errors)
    assert "author" in _fields(errors)


def test_missing_template_field(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('template: "tcc-abnt"\n', "")
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert "missing" in _codes(errors)
    assert "template" in _fields(errors)


def test_missing_tcc_required_year(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('year: "2026"\n', "")
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert "year" in _fields(errors)


def test_missing_artigo_abnt_institution(tmp_path: Path) -> None:
    fm = 'title: "Artigo"\nauthor: "Ana"\ntemplate: "artigo-abnt"\nlang: "pt-BR"\n'
    p = _write_md(tmp_path, fm)
    errors = validate(p, "artigo-abnt")
    assert "institution" in _fields(errors)


def test_artigo_ieee_does_not_require_institution(tmp_path: Path) -> None:
    p = _write_md(tmp_path, IEEE_VALID)
    errors = validate(p, "artigo-ieee")
    assert "institution" not in _fields(errors)


# ---------------------------------------------------------------------------
# Placeholder detection
# ---------------------------------------------------------------------------

def test_placeholder_title_tcc(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('title: "Meu TCC"', 'title: "T\u00edtulo do TCC"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    placeholder_fields = [e.field for e in errors if e.code == "placeholder"]
    assert "title" in placeholder_fields


def test_placeholder_author(tmp_path: Path) -> None:
    fm = IEEE_VALID.replace('author: "John Doe"', 'author: "Author"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "artigo-ieee")
    placeholder_fields = [e.field for e in errors if e.code == "placeholder"]
    assert "author" in placeholder_fields


def test_placeholder_advisor(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('advisor: "Prof. Dr. Joao Costa"', 'advisor: "Prof. Dr. Nome do Orientador"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    placeholder_fields = [e.field for e in errors if e.code == "placeholder"]
    assert "advisor" in placeholder_fields


# ---------------------------------------------------------------------------
# Template mismatch
# ---------------------------------------------------------------------------

def test_template_mismatch(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('template: "tcc-abnt"', 'template: "artigo-abnt"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    mismatch = [e for e in errors if e.code == "template_mismatch"]
    assert len(mismatch) == 1
    assert "artigo-abnt" in mismatch[0].message


def test_no_template_mismatch_when_matching(tmp_path: Path) -> None:
    p = _write_md(tmp_path, TCC_VALID)
    errors = validate(p, "tcc-abnt")
    assert not any(e.code == "template_mismatch" for e in errors)


# ---------------------------------------------------------------------------
# lang validation
# ---------------------------------------------------------------------------

def test_valid_lang_pt_br(tmp_path: Path) -> None:
    p = _write_md(tmp_path, TCC_VALID)
    errors = validate(p, "tcc-abnt")
    assert not any(e.code == "invalid_lang" for e in errors)


def test_valid_lang_portuguese(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('lang: "pt-BR"', 'lang: "portuguese"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert not any(e.code == "invalid_lang" for e in errors)


def test_valid_lang_en_us(tmp_path: Path) -> None:
    p = _write_md(tmp_path, IEEE_VALID)
    errors = validate(p, "artigo-ieee")
    assert not any(e.code == "invalid_lang" for e in errors)


def test_invalid_lang(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('lang: "pt-BR"', 'lang: "xx-ZZ"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    invalid = [e for e in errors if e.code == "invalid_lang"]
    assert len(invalid) == 1
    assert "xx-ZZ" in invalid[0].message


def test_missing_lang_does_not_trigger_invalid_lang(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('lang: "pt-BR"\n', "")
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    assert not any(e.code == "invalid_lang" for e in errors)


# ---------------------------------------------------------------------------
# Author as list-of-dicts (tcc-abnt style)
# ---------------------------------------------------------------------------

def test_author_list_of_dicts_accepted(tmp_path: Path) -> None:
    p = _write_md(tmp_path, TCC_VALID)
    errors = validate(p, "tcc-abnt")
    assert not any(e.field == "author" for e in errors)


def test_author_list_placeholder_flagged(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('  - name: "Maria Silva"', '  - name: "Nome Completo do Autor"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    placeholder_fields = [e.field for e in errors if e.code == "placeholder"]
    assert "author" in placeholder_fields


# ---------------------------------------------------------------------------
# Multiple errors
# ---------------------------------------------------------------------------

def test_multiple_errors_returned(tmp_path: Path) -> None:
    fm = TCC_VALID.replace('title: "Meu TCC"\n', "").replace('lang: "pt-BR"', 'lang: "xx-ZZ"')
    p = _write_md(tmp_path, fm)
    errors = validate(p, "tcc-abnt")
    codes = _codes(errors)
    assert "missing" in codes
    assert "invalid_lang" in codes
