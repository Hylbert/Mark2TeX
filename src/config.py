from __future__ import annotations

import json
from pathlib import Path

from platformdirs import user_config_dir

CONFIG_DIR  = Path(user_config_dir("mark2tex", appauthor=False))
CONFIG_FILE = CONFIG_DIR / "config.json"

SUPPORTED_LANGUAGES: dict[str, str] = {
    "pt_BR": "Português (Brasil)",
    "en_US": "English",
}

# Temas: chave interna -> nome exibido
SUPPORTED_THEMES: dict[str, str] = {
    "default": "Default",
    "nord":    "Nord",
    "dracula": "Dracula",
    "solarized": "Solarized",
    "gruvbox": "Gruvbox",
}

DEFAULTS: dict = {
    "language": "pt_BR",
    "theme":    "default",
}


def load() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULTS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULTS)


def save(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
