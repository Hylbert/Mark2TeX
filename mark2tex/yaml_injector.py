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

# Captures a simple scalar YAML field: key: "value" or key: value
_FIELD_RE = re.compile(r'^(?P<key>[\w-]+):\s*(?P<value>.+)$', re.MULTILINE)

_TEMPLATE_FIELDS: dict[str, dict[str, str]] = {
    "tcc-abnt": {
        "title": "Título do TCC",
        "author": "Autor",
        "date": "",
        "template": "tcc-abnt",
        "lang": "pt-BR",
        "year": "",
        "institution": "Nome da Instituição de Ensino",
        "course": "Nome do Curso",
        "advisor": "Prof. Dr. Nome do Orientador",
    },
    "artigo-abnt": {
        "title": "Título do Artigo",
        "author": "Autor",
        "date": "",
        "template": "artigo-abnt",
        "lang": "pt-BR",
        "institution": "Nome da Instituição de Ensino",
    },
    "artigo-ieee": {
        "title": "Article Title",
        "author": "Author",
        "date": "",
        "template": "artigo-ieee",
        # babel uses its own language names, not BCP-47 locale codes.
        # 'english' maps to American English in babel (same as 'american').
        "lang": "english",
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
    # --- new templates ---
    "dissertacao-abnt": {
        "title": "Título da Dissertação",
        "author": "Autor",
        "date": "",
        "template": "dissertacao-abnt",
        "lang": "pt-BR",
        "year": "",
        "institution": "Nome da Instituição de Ensino",
        "program": "Programa de Pós-Graduação em Nome da Área",
        "advisor": "Prof. Dr. Nome do Orientador",
        "degree": "Mestre em Nome da Área",
    },
    "relatorio-abnt": {
        "title": "Título do Relatório",
        "author": "Autor",
        "date": "",
        "template": "relatorio-abnt",
        "lang": "pt-BR",
        "institution": "Nome da Instituição de Ensino",
        "course": "Nome do Curso",
        "report-type": "Relatório de Estágio Supervisionado",
    },
    "artigo-acm": {
        "title": "Article Title",
        "author": "Author",
        "date": "",
        "template": "artigo-acm",
        # acmart uses babel internally; 'english' is the safe default.
        "lang": "english",
    },
    "tese-abnt": {
        "title": "Título da Tese",
        "author": "Autor",
        "date": "",
        "template": "tese-abnt",
        "lang": "pt-BR",
        "year": "",
        "institution": "Nome da Instituição de Ensino",
        "program": "Programa de Pós-Graduação em Nome da Área",
        "advisor": "Prof. Dr. Nome do Orientador",
        "degree": "Doutor em Nome da Área",
    },
    "artigo-apa": {
        "title": "Article Title in APA Style",
        "author": "Author",
        "date": "",
        "template": "artigo-apa",
        "lang": "english",
        "institution": "Institution name",
    },
    "notas-aula": {
        "title": "Notas de Aula",
        "author": "Seu Nome",
        "date": "",
        "template": "notas-aula",
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

# Fields that are template-specific (not universal) — used by swap_template
# to decide what to add/remove when changing templates.
_COMMON_FIELDS: frozenset[str] = frozenset({"title", "author", "date", "lang"})


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


def _parse_scalar_fields(fm_block: str) -> dict[str, str]:
    """Extract simple key: value pairs from a raw frontmatter block string.

    Handles quoted and unquoted values. Multi-line / list fields (e.g.
    author as a YAML list) are skipped intentionally — swap_template only
    patches scalar fields.
    """
    fields: dict[str, str] = {}
    for m in _FIELD_RE.finditer(fm_block):
        key = m.group("key")
        raw = m.group("value").strip()
        # Strip surrounding quotes if present
        if (raw.startswith('"') and raw.endswith('"')) or \
           (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1]
        fields[key] = raw
    return fields


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


def swap_template(file_path: str | Path, new_template: str) -> bool:
    """Update the frontmatter of *file_path* to *new_template* surgically.

    Rules:
    - ``template:`` and ``date:`` are always updated.
    - Fields shared between old and new template keep the user's current value.
    - Fields exclusive to the new template are appended with their placeholder.
    - Fields exclusive to the old template (not in new template) are removed.
    - Common fields (title, author, date, lang) are always preserved.

    Returns True on success, False on any I/O or parse error.
    Never raises.
    """
    path = Path(file_path).resolve()
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    fm_match = _FRONTMATTER_RE.match(content)
    if not fm_match:
        return False  # No frontmatter to patch — caller should use inject_frontmatter

    fm_raw = fm_match.group(0)  # includes opening/closing ---
    body = content[fm_match.end():]

    # Current scalar values in the frontmatter
    current_values = _parse_scalar_fields(fm_raw)

    # Fields defined for the new template
    new_template_fields = dict(_TEMPLATE_FIELDS.get(new_template, _DEFAULT_FIELDS))
    new_template_fields["template"] = new_template
    new_template_fields["date"] = date.today().isoformat()

    # Build the merged field set:
    # 1. Start with new template field order
    # 2. For each field, prefer the user's current value unless it's a
    #    template-specific field not in the old frontmatter at all (new addition)
    merged: dict[str, str] = {}
    for key, placeholder in new_template_fields.items():
        if key in ("template", "date"):
            merged[key] = new_template_fields[key]
        elif key in current_values:
            # User may have filled this in — keep their value
            merged[key] = current_values[key]
        else:
            # Field is new to this template — insert placeholder
            merged[key] = placeholder

    # Build new frontmatter block
    lines = ["---"]
    for key, value in merged.items():
        lines.append(f'{key}: "{value}"')
    lines.append("---")
    lines.append("")
    new_fm = "\n".join(lines) + "\n"

    try:
        path.write_text(new_fm + body, encoding="utf-8")
        return True
    except OSError:
        return False


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
