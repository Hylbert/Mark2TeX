"""Template metadata loader for Mark2TeX.

Reads template.yaml files from the templates directory and exposes a
small, typed structure for the CLI and TUI to consume without coupling
business logic to YAML or disk layout details.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


@dataclass(frozen=True)
class TemplateMeta:
    slug: str
    name: str
    norm: str | None = None
    document_type: str | None = None
    level: str | None = None
    language: str | None = None
    description: str | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def load_template_meta(templates_dir: Path) -> dict[str, TemplateMeta]:
    """Load metadata for all templates under *templates_dir*.

    The key of the returned dict is always the template slug (directory
    name).  If template.yaml is missing or invalid, a minimal TemplateMeta
    is returned with ``name == slug`` and other fields set to None.
    """
    result: dict[str, TemplateMeta] = {}

    if not templates_dir.is_dir():
        return result

    for entry in templates_dir.iterdir():
        if not entry.is_dir():
            continue
        slug = entry.name
        meta_path = entry / "template.yaml"
        raw = _load_yaml(meta_path)
        name = str(raw.get("name") or slug)
        norm = raw.get("norm")
        dtype = raw.get("document_type")
        level = raw.get("level")
        lang = raw.get("language")
        desc = raw.get("description")
        result[slug] = TemplateMeta(
            slug=slug,
            name=name,
            norm=str(norm) if norm else None,
            document_type=str(dtype) if dtype else None,
            level=str(level) if level else None,
            language=str(lang) if lang else None,
            description=str(desc) if desc else None,
        )

    return result
