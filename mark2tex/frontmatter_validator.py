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
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ImportError(
        "PyYAML is required by mark2tex.frontmatter_validator. "
        "Install it with: pip install PyYAML"
    ) from exc

from .i18n import t

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

# Matches the opening --- and captures everything up to the closing ---.
# Flags:
#   re.DOTALL   — . matches newlines inside the YAML block
#   re.MULTILINE — ^ matches the very start of the string
# The closing delimiter accepts an optional leading newline (\n?) so it
# works whether or not the last YAML field line ends with an extra blank line.
_FRONTMATTER_RE = re.compile(
    r"^---[ \t]*\r?\n(.*?)\r?\n?---[ \t]*\r?\n",
    re.DOTALL | re.MULTILINE,
)

# Fields required for every template
_REQUIRED_COMMON: tuple[str, ...] = ("title", "author", "template")

# Extra required fields per template
_REQUIRED_EXTRA: dict[str, tuple[str, ...]] = {
    "tcc-abnt":        ("year", "institution", "course", "advisor"),
    "artigo-abnt":     ("institution",),
    "artigo-ieee":     (),
    "doc-tecnica":     (),
    # --- new templates ---
    "dissertacao-abnt": ("year", "institution", "program", "advisor"),
    "relatorio-abnt":   ("institution",),
    "artigo-acm":       (),
    "tese-abnt":        ("year", "institution", "program", "advisor"),
    "artigo-apa":       (),
    "notas-aula":       (),
}

# Default placeholder values copied from yaml_injector._TEMPLATE_FIELDS
_PLACEHOLDERS: frozenset[str] = frozenset({
    "Título do TCC",
    "Título do Artigo",
    "Article Title",
    "Documento Técnico",
    "Título do Projeto",
    "Autor",
    "Author",
    "Nome Completo do Autor",
    "Nome do Orientador",
    "Prof. Dr. Nome do Orientador",
    "Nome da Instituição de Ensino",
    "Nome do Curso",
    "Nome do Departamento",
    "Nome do Campus",
    # new templates
    "Título da Dissertação",
    "Título do Relatório",
    "Programa de Pós-Graduação em Nome da Área",
    "Mestre em Nome da Área",
    "Relatório de Estágio Supervisionado",
    "Título da Tese",
    "Doutor em Nome da Área",
    "Notas de Aula",
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

    Messages are resolved via t() at call-time so the active language is
    always respected.
    """
    path = Path(file_path)
    errors: list[ValidationError] = []

    data = _extract_yaml(path)
    if data is None:
        return [
            ValidationError(
                field="frontmatter",
                code="parse_error",
                message=t("validator.parse_error"),
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
                message=t("validator.missing").format(field=field),
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
                message=t("validator.placeholder").format(field=field),
            ))

    # ------------------------------------------------------------------ #
    # 3. template field must match selected template
    # ------------------------------------------------------------------ #
    fm_template = _str_value(data, "template")
    if fm_template and fm_template != selected_template:
        errors.append(ValidationError(
            field="template",
            code="template_mismatch",
            message=t("validator.template_mismatch").format(
                fm_template=fm_template,
                selected=selected_template,
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
            message=t("validator.invalid_lang").format(
                lang=lang,
                accepted=", ".join(sorted(_VALID_LANGS)),
            ),
        ))

    return errors
