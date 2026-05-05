import json
import os

from rich.text import Text
from textual.app import RenderResult
from textual.widget import Widget
from textual.widgets import ListItem, Static

# ---------------------------------------------------------------------------
# JSON-based assets (logo.json / icon.json)
# ---------------------------------------------------------------------------


def _render_art(asset_path: str) -> Text:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, "assets", asset_path)
    try:
        with open(full_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return Text(f"Error loading asset {asset_path}: {e}", style="red")
    out = Text()
    for item in data:
        if item.get("type") == "newline":
            out.append("\n")
        else:
            out.append(item.get("char", ""), style=item.get("color"))
    return out


def render_logo() -> Text:
    return _render_art("logo.json")


def render_icon() -> Text:
    return _render_art("icon.json")


# ---------------------------------------------------------------------------
# Gradiente helpers
# ---------------------------------------------------------------------------

_BOX_CHARS = set("█╗╔╝╚║═╠╣╦╩╬╟╙╘╒╓╫╪┼┤├┴┬┼─│")


def _lerp(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _grad_color_from(palette: list, t: float) -> str:
    t = max(0.0, min(1.0, t))
    s = t * (len(palette) - 1)
    i = int(s)
    r, g, b = palette[-1] if i >= len(palette) - 1 else _lerp(palette[i], palette[i + 1], s - i)
    return f"rgb({r},{g},{b})"


def _render_block(lines: list, palette: list, text: Text) -> None:
    for row_idx, line in enumerate(lines):
        width = len(line)
        t_v = row_idx / max(len(lines) - 1, 1)
        for col_idx, ch in enumerate(line):
            t_h = col_idx / max(width - 1, 1)
            t = t_v * 0.7 + t_h * 0.3
            color = _grad_color_from(palette, t)
            style = f"bold {color}" if ch in _BOX_CHARS else "rgb(40,45,48)"
            text.append(ch, style=style)
        if row_idx < len(lines) - 1:
            text.append("\n")


# ---------------------------------------------------------------------------
# Banner: MARK2 (laranja) + TEX (teal)
# ---------------------------------------------------------------------------

_BANNER_MARK2 = [
    "███╗   ███╗ █████╗ ██████╗ ██╗  ██╗",
    "████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝",
    "██╔████╔██║███████║██████╔╝█████╔╝ ",
    "██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ",
    "██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗",
    "╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝",
]

_BANNER_TEX = [
    "██████╗ ████████╗███████╗██╗  ██╗",
    "╚════██╗╚══██╔══╝██╔════╝╚██╗██╔╝",
    " █████╔╝   ██║   █████╗   ╚███╔╝ ",
    "██╔═══╝    ██║   ██╔══╝   ██╔██╗ ",
    "███████╗   ██║   ███████╗██╔╝ ██╗",
    "╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝",
]

_GRAD_MARK2 = [
    (3, 101, 107),
    (3, 101, 107),
    (40, 122, 128),
    (40, 122, 128),
    (90, 155, 160),
    (90, 155, 160),
]

_GRAD_TEX = [
    (250, 250, 250),
    (250, 250, 250),
    (200, 220, 221),
    (200, 220, 221),
    (150, 190, 193),
    (150, 190, 193),
]


def _read_version() -> str:
    try:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(base, "pyproject.toml")) as f:
            for line in f:
                if line.strip().startswith("version"):
                    return line.split("=")[1].strip().strip('"')
    except Exception:
        pass
    return "0.1.0"


_VERSION = _read_version()


class M2TBannerWidget(Widget):
    DEFAULT_CSS = """
    M2TBannerWidget {
        height: auto;
        width: 100%;
        content-align: center middle;
        padding: 1 2 0 2;
    }
    """

    def render(self) -> RenderResult:
        text = Text(justify="center", no_wrap=True)

        _render_block(_BANNER_MARK2, _GRAD_MARK2, text)
        text.append("\n\n")
        _render_block(_BANNER_TEX, _GRAD_TEX, text)

        version_str = f"v{_VERSION}"
        subtitle = "Markdown → LaTeX/PDF  ·  "
        text.append(f"\n\n{subtitle}  ", style="rgb(110,115,120) italic")
        text.append(version_str, style="bold rgb(255,255,255)")

        return text


# ---------------------------------------------------------------------------
# M2TMenuOption — ASCII art single ↔ double ao highlight
# ---------------------------------------------------------------------------

_MENU_ART: dict[str, tuple[str, str]] = {
    # ── Português ──────────────────────────────────────────────────────────
    "AJUDA": (
        "┌─┐   ┬ ┬ ┬ ┌┬┐ ┌─┐\n├─┤   │ │ │  ││ ├─┤\n┴ ┴ └─┘ └─┘ ─┴┘ ┴ ┴",
        "╔═╗   ╦ ╦ ╦ ╔╦╗ ╔═╗\n╠═╣   ║ ║ ║  ║║ ╠═╣\n╩ ╩ ╚═╝ ╚═╝ ═╩╝ ╩ ╩",
    ),
    "SAIR": (
        "┌─┐ ┌─┐ ┬ ┬─┐\n└─┐ ├─┤ │ │┬┘\n└─┘ ┴ ┴ ┴ ┴└─",
        "╔═╗ ╔═╗ ╦ ╦═╗\n╚═╗ ╠═╣ ║ ║╔╝\n╚═╝ ╩ ╩ ╩ ╩╚═",
    ),
    "AJUSTES": (
        "┌─┐   ┬ ┬ ┬ ┌─┐ ┌┬┐ ┌─┐ ┌─┐\n├─┤   │ │ │ └─┐  │  ├┤  └─┐\n┴ ┴ └─┘ └─┘ └─┘  ┴  └─┘ └─┘",
        "╔═╗   ╦ ╦ ╦ ╔═╗ ╔╦╗ ╔═╗ ╔═╗\n╠═╣   ║ ║ ║ ╚═╗  ║  ╠╣  ╚═╗\n╩ ╩ ╚═╝ ╚═╝ ╚═╝  ╩  ╚═╝ ╚═╝",
    ),
    # ── English ────────────────────────────────────────────────────────────
    "SETTINGS": (
        "┌─┐ ┌─┐ ┌┬┐ ┌┬┐ ┬ ┌┐┌ ┌─┐ ┌─┐\n└─┐ ├┤   │   │  │ │││ │ ┬ └─┐\n└─┘ └─┘  ┴   ┴  ┴ ┘└┘ └─┘ └─┘",
        "╔═╗ ╔═╗ ╔╦╗ ╔╦╗ ╦ ╔╗╔ ╔═╗ ╔═╗\n╚═╗ ╠╣   ║   ║  ║ ║║║ ║ ╦ ╚═╗\n╚═╝ ╚═╝  ╩   ╩  ╩ ╝╚╝ ╚═╝ ╚═╝",
    ),
    "HELP": (
        "┬ ┬ ┌─┐ ┬  ┌─┐\n├─┤ ├┤  │  ├─┘\n┴ ┴ └─┘ ┴─┘┴  ",
        "╦ ╦ ╔═╗ ╦  ╔═╗\n╠═╣ ╠╣  ║  ╠═╝\n╩ ╩ ╚═╝ ╩═╝╩  ",
    ),
    "EXIT": (
        "┌─┐ ┬ ┬ ┬┌┬┐\n│─┼┐│ │ │ │ \n└─┘└└─┘ ┴ ┴ ",
        "╔═╗ ╦ ╦ ╦╔╦╗\n║═╬╗║ ║ ║ ║ \n╚═╝╚╚═╝ ╩ ╩ ",
    ),
}


class M2TMenuOption(ListItem):
    """
    ListItem com ASCII art que troca de estilo ao ser highlighted:
    - Normal:   box single-line
    - Selected: box double-line
    """

    def __init__(self, label_key: str, item_id: str | None = None) -> None:
        super().__init__(id=item_id)
        self._key = label_key
        self._arts = _MENU_ART.get(label_key, (label_key, label_key))

    def compose(self):
        yield Static(self._arts[0], id=f"art-{self._key}", classes="menu-art-label menu-art-normal")

    def watch_highlighted(self, value: bool) -> None:
        try:
            art = self.query_one(f"#art-{self._key}", Static)
            if value:
                art.update(self._arts[1])
                art.set_classes("menu-art-label menu-art-selected")
            else:
                art.update(self._arts[0])
                art.set_classes("menu-art-label menu-art-normal")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# M2TSettingsOption — opção de seleção única (● / ○) para telas de settings
# ---------------------------------------------------------------------------


class M2TSettingsOption(ListItem):
    """
    ListItem para opções de settings.
    Troca ○ → ● visualmente via mark_selected().
    """

    def __init__(self, label: str, value: str, selected: bool = False) -> None:
        super().__init__(id=f"opt-{value}")
        self._label = label
        self._value = value
        self._selected = selected

    def compose(self):
        prefix = "● " if self._selected else "○ "
        yield Static(
            prefix + self._label,
            id=f"static-{self._value}",
            classes="settings-option",
        )

    def mark_selected(self, yes: bool) -> None:
        try:
            s = self.query_one(f"#static-{self._value}", Static)
            s.update(("● " if yes else "○ ") + self._label)
        except Exception:
            pass
