import json
import os
from rich.text import Text

def _render_art(asset_path: str) -> Text:
    """Carrega a arte de um arquivo JSON e a converte em rich.Text."""
    # Resolve o caminho absoluto para evitar problemas com CWD
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, "assets", asset_path)

    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return Text(f"Error loading asset {asset_path}: {e}", style="red")

    out = Text()
    for item in data:
        if item.get("type") == "newline":
            out.append("\n")
        else:
            char = item.get("char", "")
            color = item.get("color")
            out.append(char, style=color)

    return out

def render_logo() -> Text:
    """Renderiza o logo principal do Mark2TeX."""
    return _render_art("logo.json")

def render_icon() -> Text:
    """Renderiza o ícone compacto do Mark2TeX."""
    return _render_art("icon.json")
