"""Tests for mark2tex.yaml_injector."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from mark2tex.yaml_injector import (
    build_frontmatter,
    has_backup,
    has_frontmatter,
    inject_frontmatter,
    restore_file,
    swap_template,
)

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
    """Non-existent file should not trigger injection (safe default)."""
    f = tmp_path / "missing.md"
    assert has_frontmatter(f) is True


# ---------------------------------------------------------------------------
# build_frontmatter
# ---------------------------------------------------------------------------

def test_build_frontmatter_contains_template_key() -> None:
    fm = build_frontmatter("tcc-abnt")
    assert 'template: "tcc-abnt"' in fm


def test_build_frontmatter_contains_lang_for_artigo_ieee() -> None:
    # babel does not accept BCP-47 codes; the default must be 'english'
    fm = build_frontmatter("artigo-ieee")
    assert 'lang: "english"' in fm


def test_build_frontmatter_starts_and_ends_with_dashes() -> None:
    fm = build_frontmatter("doc-tecnica")
    lines = fm.strip().splitlines()
    assert lines[0] == "---"
    assert lines[-1] == "---"


def test_build_frontmatter_unknown_template_uses_defaults() -> None:
    fm = build_frontmatter("unknown-template")
    assert 'template: "unknown-template"' in fm


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
    """Re-injection (template switch) should replace frontmatter without new backup."""
    f = tmp_path / "doc.md"
    f.write_text('---\ntitle: "Old"\ntemplate: "tcc-abnt"\n---\n\n# Content\n', encoding="utf-8")
    bak_dir = tmp_path / "backups"

    with patch("mark2tex.yaml_injector._backup_dir", return_value=bak_dir):
        bak_dir.mkdir(parents=True, exist_ok=True)
        inject_frontmatter(f, "artigo-ieee")

    content = f.read_text(encoding="utf-8")
    assert 'template: "artigo-ieee"' in content
    bak_files = list(bak_dir.glob("*.bak"))
    assert len(bak_files) == 0


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
    """title, author and lang filled by the user must survive a template swap."""
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "My Real Title"\nauthor: "Hylbert"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    result = swap_template(f, "doc-tecnica")
    content = f.read_text(encoding="utf-8")

    assert result is True
    assert 'title: "My Real Title"' in content
    assert 'author: "Hylbert"' in content
    assert 'lang: "en-US"' in content


def test_swap_updates_template_field(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-ieee"\nlang: "en-US"\n---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "doc-tecnica")
    content = f.read_text(encoding="utf-8")

    assert 'template: "doc-tecnica"' in content
    assert 'template: "artigo-ieee"' not in content


def test_swap_adds_new_exclusive_fields_with_placeholder(tmp_path: Path) -> None:
    """Swapping to tcc-abnt must add advisor/institution/course/year."""
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
    """Swapping from tcc-abnt to artigo-ieee must drop advisor/institution/course/year."""
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
    """institution is in both artigo-abnt and tcc-abnt; user value must survive."""
    f = tmp_path / "doc.md"
    f.write_text(
        '---\ntitle: "T"\nauthor: "A"\ndate: "2026-01-01"\n'
        'template: "artigo-abnt"\nlang: "pt-BR"\ninstitution: "UFAM"\n'
        '---\n\n# Body\n',
        encoding="utf-8",
    )
    swap_template(f, "tcc-abnt")
    content = f.read_text(encoding="utf-8")

    assert 'institution: "UFAM"' in content


def test_swap_returns_false_when_no_frontmatter(tmp_path: Path) -> None:
    """Files without frontmatter must be left untouched; returns False."""
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
    """The markdown body after the closing --- must not be touched."""
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
