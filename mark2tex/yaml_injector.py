"""YAML frontmatter injection, backup and restore for Mark2TeX."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

from platformdirs import user_data_dir

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

_TEMPLATE_FIELDS: dict[str, dict[str, str]] = {
    "tcc-abnt": {
        "title": "Título do TCC",
        "author": "Autor",
        "date": "",
        "template": "tcc-abnt",
        "lang": "pt-BR",
    },
    "artigo-abnt": {
        "title": "Título do Artigo",
        "author": "Autor",
        "date": "",
        "template": "artigo-abnt",
        "lang": "pt-BR",
    },
    "artigo-ieee": {
        "title": "Article Title",
        "author": "Author",
        "date": "",
        "template": "artigo-ieee",
        "lang": "en-US",
    },
    "doc-tecnica": {
        "title": "Documento Técnico",
        "author": "Autor",
        "date": "",
        "template": "doc-tecnica",
        "lang": "pt-BR",
    },
    "projeto": {
        "title": "Título do Projeto",
        "author": "Autor",
        "date": "",
        "template": "projeto",
        "lang": "pt-BR",
    },
}

_DEFAULT_FIELDS: dict[str, str] = {
    "title": "Documento",
    "author": "Autor",
    "date": "",
    "template": "",
    "lang": "pt-BR",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _backup_dir() -> Path:
    p = Path(user_data_dir("mark2tex", appauthor=False)) / "backups"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _index_path() -> Path:
    return _backup_dir() / "index.json"


def _load_index() -> dict[str, Any]:
    idx = _index_path()
    if idx.exists():
        try:
            return cast(dict[str, Any], json.loads(idx.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_index(data: dict) -> None:
    _index_path().write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _bak_filename(file_path: Path) -> str:
    """Convert an absolute path to a safe backup filename."""
    return str(file_path.resolve()).replace("/", "_").replace("\\", "_").replace(":", "_") + ".bak"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def has_frontmatter(file_path: str | Path) -> bool:
    """Return True if the .md file already starts with a YAML frontmatter block."""
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        return bool(_FRONTMATTER_RE.match(content))
    except (OSError, UnicodeDecodeError):
        return True  # Do not prompt if unreadable


def build_frontmatter(template: str) -> str:
    """Return a YAML frontmatter block string for the given template."""
    fields = dict(_TEMPLATE_FIELDS.get(template, _DEFAULT_FIELDS))
    fields["template"] = template
    fields["date"] = date.today().isoformat()
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f'{key}: "{value}"')
    lines.append("---")
    lines.append("")  # blank line after closing ---
    return "\n".join(lines) + "\n"


def inject_frontmatter(file_path: str | Path, template: str) -> bool:
    """Inject (or replace) YAML frontmatter in *file_path*.

    - Creates a backup before modifying if the file has no frontmatter yet.
    - If the file already has frontmatter, replaces it silently (no new backup).
    - Returns True on success, False on error.
    """
    path = Path(file_path).resolve()
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    already_has = bool(_FRONTMATTER_RE.match(content))
    new_fm = build_frontmatter(template)

    if already_has:
        # Silent replace — user was already warned on the first injection
        new_content = _FRONTMATTER_RE.sub(new_fm, content, count=1)
    else:
        # First injection — save backup
        bak_name = _bak_filename(path)
        bak_path = _backup_dir() / bak_name
        try:
            bak_path.write_bytes(path.read_bytes())
        except OSError:
            return False
        # Update index
        idx = _load_index()
        idx[bak_name] = {
            "original_path": str(path),
            "created_at": date.today().isoformat(),
            "template": template,
        }
        _save_index(idx)
        new_content = new_fm + content

    try:
        path.write_text(new_content, encoding="utf-8")
        return True
    except OSError:
        return False


def restore_file(file_path: str | Path) -> tuple[bool, str]:
    """Restore *file_path* to its pre-injection state.

    Returns (success, message).
    """
    path = Path(file_path).resolve()
    bak_name = _bak_filename(path)
    bak_path = _backup_dir() / bak_name
    idx = _load_index()

    if bak_name not in idx or not bak_path.exists():
        return False, f"No backup found for '{path.name}'."

    try:
        path.write_bytes(bak_path.read_bytes())
        bak_path.unlink(missing_ok=True)
        del idx[bak_name]
        _save_index(idx)
        return True, f"'{path.name}' restored to its original state."
    except OSError as exc:
        return False, str(exc)


def has_backup(file_path: str | Path) -> bool:
    """Return True if a backup exists for *file_path*."""
    path = Path(file_path).resolve()
    bak_name = _bak_filename(path)
    idx = _load_index()
    return bak_name in idx
