"""Unit tests for mark2tex.utils.doc_structure.extract_sections.

Covers:
- Empty / missing / unreadable file → returns []
- h1, h2, h3 indentation and sequential numbering
- YAML frontmatter stripped before scanning
- Inline formatting (bold, italic, code) removed from heading text
- Hard cap of 30 entries
- File with only body text (no headings) → returns []
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mark2tex.utils.doc_structure import extract_sections

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def md_file(tmp_path):
    """Return a factory that writes content to a temp .md file."""
    def _write(content: str) -> Path:
        p = tmp_path / "doc.md"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


# ---------------------------------------------------------------------------
# Edge cases — empty / missing / unreadable
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_missing_file_returns_empty(self, tmp_path):
        result = extract_sections(tmp_path / "nonexistent.md")
        assert result == []

    def test_empty_file_returns_empty(self, md_file):
        result = extract_sections(md_file(""))
        assert result == []

    def test_body_only_no_headings_returns_empty(self, md_file):
        content = "This is just a paragraph.\nNo headings here at all.\n"
        result = extract_sections(md_file(content))
        assert result == []

    def test_unreadable_file_returns_empty(self, tmp_path, monkeypatch):
        p = tmp_path / "unreadable.md"
        p.write_text("# Title", encoding="utf-8")
        monkeypatch.setattr(Path, "read_text", lambda *a, **kw: (_ for _ in ()).throw(PermissionError))
        result = extract_sections(p)
        assert result == []


# ---------------------------------------------------------------------------
# Heading levels and indentation
# ---------------------------------------------------------------------------

class TestHeadingLevels:
    def test_h1_no_indent(self, md_file):
        sections = extract_sections(md_file("# Introduction\n"))
        assert sections == ["1. Introduction"]

    def test_h2_two_space_indent(self, md_file):
        sections = extract_sections(md_file("## Methods\n"))
        assert sections == ["  1. Methods"]

    def test_h3_four_space_indent(self, md_file):
        sections = extract_sections(md_file("### Details\n"))
        assert sections == ["    1. Details"]

    def test_mixed_levels_sequential_numbering(self, md_file):
        content = "# First\n## Sub\n### Deep\n# Second\n"
        sections = extract_sections(md_file(content))
        assert sections[0] == "1. First"
        assert sections[1] == "  2. Sub"
        assert sections[2] == "    3. Deep"
        assert sections[3] == "4. Second"

    def test_multiple_h1_numbered_sequentially(self, md_file):
        content = "# Alpha\n# Beta\n# Gamma\n"
        sections = extract_sections(md_file(content))
        assert sections == ["1. Alpha", "2. Beta", "3. Gamma"]

    def test_h4_and_above_not_matched(self, md_file):
        """Regex only matches h1–h3; h4+ should be ignored."""
        content = "#### Not a heading\n# Real\n"
        sections = extract_sections(md_file(content))
        assert sections == ["1. Real"]


# ---------------------------------------------------------------------------
# YAML frontmatter
# ---------------------------------------------------------------------------

class TestFrontmatter:
    def test_title_key_in_frontmatter_ignored(self, md_file):
        content = "---\ntitle: My Document\nauthor: Someone\n---\n# Real Heading\n"
        sections = extract_sections(md_file(content))
        assert sections == ["1. Real Heading"]
        # title: must NOT appear as a section
        assert not any("My Document" in s for s in sections)

    def test_frontmatter_without_closing_delimiter_still_parses(self, md_file):
        """If the closing --- is missing the whole file is scanned.
        The opening --- line itself has no heading marker so it is ignored;
        headings in the body are still found.
        """
        content = "---\ntitle: Orphaned\n# Heading After\n"
        sections = extract_sections(md_file(content))
        assert "1. Heading After" in sections

    def test_no_frontmatter_parses_normally(self, md_file):
        content = "# Just a Heading\n"
        sections = extract_sections(md_file(content))
        assert sections == ["1. Just a Heading"]


# ---------------------------------------------------------------------------
# Inline formatting stripping
# ---------------------------------------------------------------------------

class TestInlineFormatting:
    def test_bold_double_star_stripped(self, md_file):
        sections = extract_sections(md_file("# **Bold Title**\n"))
        assert sections == ["1. Bold Title"]

    def test_italic_single_star_stripped(self, md_file):
        sections = extract_sections(md_file("# *Italic Title*\n"))
        assert sections == ["1. Italic Title"]

    def test_italic_underscore_stripped(self, md_file):
        sections = extract_sections(md_file("# _Italic Title_\n"))
        assert sections == ["1. Italic Title"]

    def test_inline_code_backtick_stripped(self, md_file):
        sections = extract_sections(md_file("# `code_func`\n"))
        assert sections == ["1. code_func"]

    def test_mixed_formatting_stripped(self, md_file):
        sections = extract_sections(md_file("# **Bold** and `code`\n"))
        assert sections == ["1. Bold and code"]


# ---------------------------------------------------------------------------
# Hard cap at 30 entries
# ---------------------------------------------------------------------------

class TestHardCap:
    def test_exactly_30_headings_all_returned(self, md_file):
        content = "".join(f"# Section {i}\n" for i in range(1, 31))
        sections = extract_sections(md_file(content))
        assert len(sections) == 30

    def test_31_headings_capped_at_30(self, md_file):
        content = "".join(f"# Section {i}\n" for i in range(1, 32))
        sections = extract_sections(md_file(content))
        assert len(sections) == 30

    def test_cap_preserves_first_30(self, md_file):
        content = "".join(f"# Section {i}\n" for i in range(1, 32))
        sections = extract_sections(md_file(content))
        assert "1. Section 1" in sections[0]
        assert "30. Section 30" in sections[29]
