"""Frontmatter validator for Mark2TeX.

Validates the YAML frontmatter block of a .md file *before* the Docker
compilation pipeline starts, giving users actionable feedback in the TUI
instead of cryptic XeLaTeX errors.

Public API
----------
    errors = validate(file_path, selected_template)
    if errors:
        for e in errors:
            print(e.message)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # PyYAML is already a transitive dep via several packages
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationError:
    field: str
    code: str   # missing | placeholder | template_mismatch | invalid_lang | parse_error
    message: str


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Fields required for every template
_REQUIRED_COMMON: tuple[str, ...] = ("title", "author", "template")

# Extra required fields per template
_REQUIRED_EXTRA: dict[str, tuple[str, ...]] = {
    "tcc-abnt":    ("year", "institution", "course", "advisor"),
    "artigo-abnt": ("institution",),
    "artigo-ieee": (),
    "doc-tecnica": (),
}

# Default placeholder values copied from yaml_injector._TEMPLATE_FIELDS
# These are flagged as "not filled in yet" regardless of template.
_PLACEHOLDERS: frozenset[str] = frozenset({
    "T\u00edtulo do TCC",
    "T\u00edtulo do Artigo",
    "Article Title",
    "Documento T\u00e9cnico",
    "T\u00edtulo do Projeto",
    "Autor",
    "Author",
    "Nome Completo do Autor",
    "Nome do Orientador",
    "Prof. Dr. Nome do Orientador",
    "Nome da Institui\u00e7\u00e3o de Ensino",
    "Nome do Curso",
    "Nome do Departamento",
    "Nome do Campus",

})

_VALID_LANGS: frozenset[str] = frozenset({
    "pt-BR", "pt_BR", "portuguese",
    "en-US", "en_US", "english",
    "es", "fr", "de",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_yaml(file_path: Path) -> dict[str, Any] | None:
    """Return parsed frontmatter dict or None if absent / unparseable."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    m = _FRONTMATTER_RE.match(content)
    if not m:
        return None

    if yaml is None:
        return None

    try:
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def _str_value(data: dict[str, Any], key: str) -> str:
    """Return the string value for a key, flattening list-of-dicts (author field)."""
    val = data.get(key)
    if val is None:
        return ""
    if isinstance(val, list):
        # author: [{name: "..."}] pattern used in tcc-abnt
        names = []
        for item in val:
            if isinstance(item, dict):
                names.append(str(item.get("name", "")).strip())
            else:
                names.append(str(item).strip())
        return ", ".join(n for n in names if n)
    return str(val).strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(file_path: str | Path, selected_template: str) -> list[ValidationError]:
    """Validate the YAML frontmatter of *file_path* against *selected_template*.

    Returns a (possibly empty) list of :class:`ValidationError`.
    Never raises — parse failures are returned as a ValidationError with
    code ``parse_error``.
    """
    path = Path(file_path)
    errors: list[ValidationError] = []

    data = _extract_yaml(path)
    if data is None:
        return [
            ValidationError(
                field="frontmatter",
                code="parse_error",
                message="Could not parse YAML frontmatter. Make sure the file starts with a valid --- block.",
            )
        ]

    # ------------------------------------------------------------------ #
    # 1. Required fields
    # ------------------------------------------------------------------ #
    required = list(_REQUIRED_COMMON) + list(_REQUIRED_EXTRA.get(selected_template, ()))
    for field in required:
        value = _str_value(data, field)
        if not value:
            errors.append(ValidationError(
                field=field,
                code="missing",
                message=f"Required field '{field}' is missing or empty.",
            ))

    # ------------------------------------------------------------------ #
    # 2. Placeholder detection
    # ------------------------------------------------------------------ #
    for field in required:
        value = _str_value(data, field)
        if value and value in _PLACEHOLDERS:
            errors.append(ValidationError(
                field=field,
                code="placeholder",
                message=f"Field '{field}' still contains the default placeholder value. Please fill it in before compiling.",
            ))

    # ------------------------------------------------------------------ #
    # 3. template field must match selected template
    # ------------------------------------------------------------------ #
    fm_template = _str_value(data, "template")
    if fm_template and fm_template != selected_template:
        errors.append(ValidationError(
            field="template",
            code="template_mismatch",
            message=(
                f"Frontmatter declares template '{fm_template}' "
                f"but the TUI has '{selected_template}' selected. "
                "Update the frontmatter or re-select the correct template."
            ),
        ))

    # ------------------------------------------------------------------ #
    # 4. lang validation
    # ------------------------------------------------------------------ #
    lang = _str_value(data, "lang")
    if lang and lang not in _VALID_LANGS:
        errors.append(ValidationError(
            field="lang",
            code="invalid_lang",
            message=(
                f"lang '{lang}' is not a recognised value. "
                f"Accepted values: {', '.join(sorted(_VALID_LANGS))}."
            ),
        ))

    return errors
