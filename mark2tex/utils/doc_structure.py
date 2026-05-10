"""doc_structure.py — Extract heading structure from a Markdown source file.

Used by the Info Panel to display the document outline after compilation.
"""
from __future__ import annotations

import re
from pathlib import Path

# Match ATX headings: # / ## / ### (levels 1-3)
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)", re.MULTILINE)

# Safety cap — avoids flooding the panel on very large documents
_MAX_SECTIONS = 30


def extract_sections(md_path: str | Path) -> list[str]:
    """Return a numbered, indented list of section labels from *md_path*.

    Headings are numbered sequentially (regardless of level) so the panel
    always shows a clean 1, 2, 3… list.  Sub-headings (## / ###) are
    indented by two spaces per extra level.

    The YAML frontmatter block (between the opening and closing ``---``)
    is stripped before scanning so that any ``title:`` key inside the
    header is not mistaken for a heading.

    Returns an empty list if the file cannot be read or contains no
    recognisable headings.
    """
    try:
        content = Path(md_path).read_text(encoding="utf-8", errors="ignore")
    except (FileNotFoundError, PermissionError, OSError):
        return []

    # Strip YAML frontmatter
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            content = content[end + 4 :]

    sections: list[str] = []
    counter = 0
    for m in _HEADING_RE.finditer(content):
        if counter >= _MAX_SECTIONS:
            break
        level = len(m.group(1))           # 1, 2, or 3
        title = m.group(2).strip()
        # Strip inline Markdown formatting (bold, italic, code)
        title = re.sub(r"[*_`]{1,2}(.+?)[*_`]{1,2}", r"\1", title)
        indent = "  " * (level - 1)
        counter += 1
        sections.append(f"{indent}{counter}. {title}")

    return sections
