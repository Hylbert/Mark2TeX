"""Tests for mark2tex.yaml_injector."""
from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import yaml

from mark2tex.yaml_injector import (
    _bak_filename,
    _parse_scalar_fields,
    _yaml_scalar,
    build_frontmatter,
    has_backup,
    has_frontmatter,
    inject_frontmatter,
    restore_file,
    swap_template,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_fm(text: str) -> dict:
    """Extract and parse the YAML frontmatter from a document string."""
    m = re.search(r'^---(.*?)---', text, re.DOTALL)
    assert m, "No frontmatter found in text"
    return yaml.safe_load(m.group(1)) or {}


# ---------------------------------------------------------------------------
# _yaml_scalar
# ---------------------------------------------------------------------------

class TestYamlScalar:
    def test_simple_value(self) -> None:
        assert _yaml_scalar("simple") == "simple"

    def test_value_with_colon_is_quoted(self) -> None:
        result = _yaml_scalar("Has: colon")
        assert ":" in result
        # Must be a valid quoted scalar (round-trip OK).
        # yaml.safe_load returns a dict when parsing "k: <value>", so index ["k"].
        assert yaml.safe_load(f"k: {result}")["k"] == "Has: colon"

    def test_empty_string(self) -> None:
        result = _yaml_scalar("")
        assert yaml.safe_load(f"k: {result}")["k"] == ""

    def test_unicode_preserved(self) -> None:
        result = _yaml_scalar("Título com acentos")
        assert yaml.safe_load(f"k: {result}")["k"] == "Título com acentos"

    def test_no_trailing_newline(self) -> None:
        assert not _yaml_scalar("hello").endswith("\n")


# ---------------------------------------------------------------------------
# _bak_filename
# ---------------------------------------------------------------------------

class TestBakFilename:
    def test_no_slashes_in_result(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        name = _bak_filename(f)
        assert "/" not in name
        assert "\\" not in name

    def test_ends_with_bak(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        assert _bak_filename(f).endswith(".bak")

    def test_two_different_paths_yield_different_names(self, tmp_path: Path) -> None:
        a = _bak_filename(tmp_path / "a.md")
        b = _bak_filename(tmp_path / "b.md")
        assert a != b


# ---------------------------------------------------------------------------
# _parse_scalar_fields
# ---------------------------------------------------------------------------

class TestParseScalarFields:
    def test_simple_unquoted(self) -> None:
        result = _parse_scalar_fields("title: My Title\nauthor: Alice\n")
        assert result["title"] == "My Title"
        assert result["author"] == "Alice"

    def test_double_quoted_value_stripped(self) -> None:
        result = _parse_scalar_fields('template: "tcc-abnt"\n')
        assert result["template"] == "tcc-abnt"

    def test_single_quoted_value_stripped(self) -> None:
        result = _parse_scalar_fields("lang: 'pt-BR'\n")
        assert result["lang"] == "pt-BR"

    def test_empty_block(self) -> None:
        assert _parse_scalar_fields("") == {}


# ---------------------------------------------------------------------------
# has_frontmatter
# ---------------------------------------------------------------------------

def test_has_frontmatter_returns_true_when_yaml_present(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("---\ntitle: \"Test\"\ntemplate: \"tcc-abnt\"\n---\n\n# Hello\n", encoding="utf-8")
    assert has_frontmatter(f) is True


def test_has_frontmatter_returns_false_when_no_yaml(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n\nSome content.", encoding="utf-8")
    assert has_frontmatter(f) is False


def test_has_frontmatter_returns_true_on_unreadable_file(tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    assert has_frontmatter(f) is True


# ---------------------------------------------------------------------------
# build_frontmatter
# ---------------------------------------------------------------------------

def test_build_frontmatter_contains_template_key() -> None:
    fm = build_frontmatter("tcc-abnt")
    data = _parse_fm(fm)
    assert data["template"] == "tcc-abnt"


def test_build_frontmatter_contains_lang_for_artigo_ieee() -> None:
    fm = build_frontmatter("artigo-ieee")
    data = _parse_fm(fm)
    assert data["lang"] == "english"


def test_build_frontmatter_starts_and_ends_with_dashes() -> None:
    fm = build_frontmatter("doc-tecnica")
    lines = fm.strip().splitlines()
    assert lines[0] == "---"
    assert lines[-1] == "---"


def test_build_frontmatter_unknown_template_uses_defaults() -> None:
    fm = build_frontmatter("unknown-template")
    data = _parse_fm(fm)
    assert data["template"] == "unknown-template"


# ---------------------------------------------------------------------------
# inject_frontmatter
# ---------------------------------------------------------------------------

def test_inject_creates_backup_on_first_injection(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# My Note\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        result = inject_frontmatter(f, "tcc-abnt")

    assert result is True
    bak_files = list(bak_dir.glob("*.bak"))
    assert len(bak_files) == 1


def test_inject_prepends_yaml_to_content(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    original = "# My Document\n\nSome text."
    f.write_text(original, encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "artigo-abnt")

    content = f.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "# My Document" in content


def test_inject_replaces_existing_yaml_silently(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text('---\ntitle: "Old"\ntemplate: "tcc-abnt"\n---\n\n# Content\n', encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "artigo-ieee")

    content = f.read_text(encoding="utf-8")
    data = _parse_fm(content)
    assert data["template"] == "artigo-ieee"
    bak_files = list(bak_dir.glob("*.bak"))
    assert len(bak_files) == 0


def test_inject_returns_false_on_missing_file(tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    with patch("mark2tex.yaml_injector._backup_dir", return_value=tmp_path / "bak"):
        result = inject_frontmatter(f, "tcc-abnt")
    assert result is False


def test_inject_returns_false_when_backup_write_fails(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"
    bak_dir.mkdir(parents=True, exist_ok=True)

    with (
        patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir),
        patch("pathlib.Path.write_bytes", side_effect=OSError("disk full")),
    ):
        result = inject_frontmatter(f, "tcc-abnt")
    assert result is False


# ---------------------------------------------------------------------------
# restore_file
# ---------------------------------------------------------------------------

def test_restore_returns_false_when_no_backup(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        (bak_dir / "index.json").write_text("{}", encoding="utf-8")
        success, msg = restore_file(f)

    assert success is False
    assert "No backup" in msg


def test_restore_recovers_original_content(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    original_content = "# Original content\n"
    f.write_text(original_content, encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "tcc-abnt")
        success, msg = restore_file(f)

    assert success is True
    assert f.read_text(encoding="utf-8") == original_content


def test_restore_removes_backup_after_restore(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "tcc-abnt")
        restore_file(f)
        bak_files = list(bak_dir.glob("*.bak"))

    assert len(bak_files) == 0


# ---------------------------------------------------------------------------
# has_backup
# ---------------------------------------------------------------------------

def test_has_backup_true_after_injection(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "tcc-abnt")
        result = has_backup(f)

    assert result is True


def test_has_backup_false_before_injection(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Hello\n", encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        (bak_dir / "index.json").write_text("{}", encoding="utf-8")
        result = has_backup(f)

    assert result is False


# ---------------------------------------------------------------------------
# swap_template
# ---------------------------------------------------------------------------

def test_swap_preserves_user_filled_common_fields(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "My Real Title"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    result = swap_template(f, "doc-tecnica")
    data = _parse_fm(f.read_text(encoding="utf-8"))
    assert result is True
    assert data["title"] == "My Real Title"
    assert data["author"] == "Hylbert"
    assert data["lang"] == "en-US"


def test_swap_updates_template_field(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "doc-tecnica")
    data = _parse_fm(f.read_text(encoding="utf-8"))
    assert data["template"] == "doc-tecnica"


def test_swap_adds_new_exclusive_fields_with_placeholder(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "My Paper"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "tcc-abnt")
    content = f.read_text(encoding="utf-8")
    assert "advisor" in content
    assert "institution" in content
    assert "course" in content
    assert "year" in content


def test_swap_removes_exclusive_fields_of_old_template(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "My TCC"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
        'template: "tcc-abnt"\nlang: "pt-BR"\nyear: "2026"\n'
        'institution: "UFAM"\ncourse: "CC"\nadvisor: "Prof. Silva"\n'
        '---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "artigo-ieee")
    content = f.read_text(encoding="utf-8")
    assert "advisor" not in content
    assert "institution" not in content
    assert "course" not in content
    assert "year" not in content


def test_swap_preserves_user_value_for_shared_exclusive_field(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-abnt"\nlang: "pt-BR"\ninstitution: "UFAM"\n'
        '---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "tcc-abnt")
    data = _parse_fm(f.read_text(encoding="utf-8"))
    assert data["institution"] == "UFAM"


def test_swap_returns_false_when_no_frontmatter(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("# Just a heading\n", encoding="utf-8")
    result = swap_template(f, "doc-tecnica")
    assert result is False
    assert f.read_text(encoding="utf-8") == "# Just a heading\n"


def test_swap_returns_false_on_missing_file(tmp_path: Path) -> None:
    f = tmp_path / "missing.md"
    result = swap_template(f, "doc-tecnica")
    assert result is False


def test_swap_body_content_preserved(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    body = "\n# Introduction\n\nThis is my document body.\n"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n' + body,
        encoding="utf-8",
    )
    swap_template(f, "doc-tecnica")
    content = f.read_text(encoding="utf-8")
    assert body in content


def test_swap_noop_when_same_template(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    original = (
        '---\ntitle: "My TCC"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
        'template: "tcc-abnt"\nlang: "pt-BR"\n---\n\n# Body\n'
    )
    f.write_text(original, encoding="utf-8")
    mtime_before = f.stat().st_mtime
    result = swap_template(f, "tcc-abnt")
    assert result is True
    assert f.stat().st_mtime == mtime_before
    assert f.read_text(encoding="utf-8") == original


def test_swap_preserves_author_list(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\nauthor:\n- name: Hylbert\n- name: Silva\ndate: "2026-01-01"\n'
        'template: "tcc-abnt"\nlang: "pt-BR"\ntitle: "T"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "dissertacao-abnt")
    data = _parse_fm(f.read_text(encoding="utf-8"))
    assert isinstance(data["author"], list)
    assert data["author"][0]["name"] == "Hylbert"
    assert data["author"][1]["name"] == "Silva"


def test_swap_preserves_multiline_block_scalar(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\ntemplate: "tcc-abnt"\n'
        'lang: "pt-BR"\nacknowledgements: |\n  Thanks to everyone.\n  Special thanks.\n---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "dissertacao-abnt")
    data = _parse_fm(f.read_text(encoding="utf-8"))
    assert "Thanks to everyone" in data["acknowledgements"]


def test_swap_graceful_on_invalid_yaml(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: [unclosed bracket\ntemplate: tcc-abnt\n---\n\n# Body\n',
        encoding="utf-8",
    )
    result = swap_template(f, "doc-tecnica")
    assert isinstance(result, bool)


def test_swap_noop_does_not_write_disk(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "doc-tecnica"\nlang: "pt-BR"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    original_content = f.read_text(encoding="utf-8")
    swap_template(f, "doc-tecnica")
    assert f.read_text(encoding="utf-8") == original_content


def test_swap_returns_false_on_write_error(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    with patch("pathlib.Path.write_text", side_effect=OSError("disk full")):
        result = swap_template(f, "doc-tecnica")
    assert result is False
