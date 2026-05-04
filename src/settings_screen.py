from __future__ import annotations

from dataclasses import dataclass, field

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static

from . import config as cfg
from .config import SUPPORTED_LANGUAGES
from .i18n import set_language, t


# ---------------------------------------------------------------------------
# Mensagens públicas
# ---------------------------------------------------------------------------

class LanguageChanged(Message):
    """Postada quando o idioma é alterado."""


# ---------------------------------------------------------------------------
# Definição de uma opção
# ---------------------------------------------------------------------------

@dataclass
class _SettingDef:
    key:       str
    value_key: str
    choices:   list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return t(f"settings.opt_{self.key}")

    @property
    def description(self) -> str:
        return t(f"settings.desc_{self.key}")


def _make_defs(available_themes: list[str]) -> list[_SettingDef]:
    return [
        _SettingDef(
            key="language",
            value_key="language",
            choices=list(SUPPORTED_LANGUAGES.values()),
        ),
        _SettingDef(
            key="theme",
            value_key="theme",
            choices=available_themes,
        ),
    ]


# ---------------------------------------------------------------------------
# Widget: linha de opção com controle ← valor →
# ---------------------------------------------------------------------------

class _OptionRow(ListItem):
    def __init__(self, definition: _SettingDef, current_label: str) -> None:
        super().__init__(id=f"opt-row-{definition.key}")
        self._def   = definition
        self._label = current_label

    def compose(self) -> ComposeResult:
        yield Static(self._def.label, id=f"opt-name-{self._def.key}", classes="opt-name")
        yield Static(
            self._arrow_line(self._label),
            id=f"opt-ctrl-{self._def.key}",
            classes="opt-ctrl",
        )

    def _arrow_line(self, val: str) -> str:
        return f"← {val} →"

    def update_value(self, new_label: str) -> None:
        self._label = new_label
        try:
            self.query_one(f"#opt-ctrl-{self._def.key}", Static).update(
                self._arrow_line(new_label)
            )
        except Exception:
            pass

    def refresh_label(self) -> None:
        try:
            self.query_one(f"#opt-name-{self._def.key}", Static).update(self._def.label)
        except Exception:
            pass

    def watch_highlighted(self, value: bool) -> None:
        try:
            name = self.query_one(f"#opt-name-{self._def.key}", Static)
            ctrl = self.query_one(f"#opt-ctrl-{self._def.key}", Static)
            if value:
                name.set_classes("opt-name opt-hl")
                ctrl.set_classes("opt-ctrl opt-ctrl-hl")
            else:
                name.set_classes("opt-name")
                ctrl.set_classes("opt-ctrl")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# SettingsScreen
# ---------------------------------------------------------------------------

class SettingsScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "close",       "Fechar"),
        Binding("left",   "prev_value",  "Valor anterior", show=False),
        Binding("right",  "next_value",  "Próximo valor",  show=False),
        Binding("1",      "tab_general", show=False),
    ]

    _TABS: list[tuple[str, str, str]] = [
        ("1", "general", "settings.tab_general"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._config  = cfg.load()
        self._active  = "general"
        self._sel_idx = 0
        # Listagem dos temas nativos do Textual — resolvida após mount
        self._defs: list[_SettingDef] = []

    # ------------------------------------------------------------------
    # on_mount: resolve temas disponíveis via app.available_themes
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        available_themes = sorted(self.app.available_themes.keys())
        self._defs = _make_defs(available_themes)
        self._rebuild_option_list()
        self.query_one("#sw-option-list", ListView).focus()
        self._update_description(0)

    def _rebuild_option_list(self) -> None:
        lv = self.query_one("#sw-option-list", ListView)
        lv.clear()
        for d in self._defs:
            lv.append(_OptionRow(d, self._raw_to_label(d)))

    # ------------------------------------------------------------------
    # Helpers valor interno ↔ rótulo
    # ------------------------------------------------------------------

    def _raw_to_label(self, d: _SettingDef) -> str:
        raw = self._config.get(d.value_key, "")
        if d.value_key == "language":
            return SUPPORTED_LANGUAGES.get(raw, raw)
        # tema: o nome interno é o próprio rótulo
        return raw

    def _label_to_raw(self, d: _SettingDef, label: str) -> str:
        if d.value_key == "language":
            return next((k for k, v in SUPPORTED_LANGUAGES.items() if v == label), label)
        return label

    # ------------------------------------------------------------------
    # Compose (estrutura vazia — lista populada em on_mount)
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Vertical(id="sw-window"):
            with Horizontal(id="sw-tabbar"):
                yield Label(" tab→ ", id="sw-tab-hint")
                for num, key, i18n_key in self._TABS:
                    active = key == self._active
                    yield Label(
                        f" [{num}{t(i18n_key)}] " if active else f"  {num}{t(i18n_key)}  ",
                        id=f"sw-tab-{key}",
                        classes="sw-tab sw-tab-active" if active else "sw-tab",
                    )

            with Horizontal(id="sw-body"):
                with Vertical(id="sw-left"):
                    yield ListView(id="sw-option-list")
                with Vertical(id="sw-right"):
                    yield Static("", id="sw-description")

            yield Label(
                f" {t('settings.saved_at')} {cfg.CONFIG_FILE} ",
                id="sw-footer",
            )

    # ------------------------------------------------------------------
    # Coluna direita: descrição
    # ------------------------------------------------------------------

    def _update_description(self, idx: int) -> None:
        if not self._defs:
            return
        self._sel_idx = idx
        self.query_one("#sw-description", Static).update(self._defs[idx].description)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id != "sw-option-list" or event.item is None:
            return
        key = event.item.id.removeprefix("opt-row-")
        idx = next((i for i, d in enumerate(self._defs) if d.key == key), 0)
        self._update_description(idx)

    # ------------------------------------------------------------------
    # Ciclar valor
    # ------------------------------------------------------------------

    def action_prev_value(self) -> None:
        self._cycle(-1)

    def action_next_value(self) -> None:
        self._cycle(1)

    @on(ListView.Selected, "#sw-option-list")
    def on_enter_pressed(self, _: ListView.Selected) -> None:
        self._cycle(1)

    def _cycle(self, direction: int) -> None:
        if not self._defs:
            return
        d       = self._defs[self._sel_idx]
        cur_lbl = self._raw_to_label(d)
        choices = d.choices
        if not choices:
            return
        cur_i   = choices.index(cur_lbl) if cur_lbl in choices else 0
        new_lbl = choices[(cur_i + direction) % len(choices)]
        new_raw = self._label_to_raw(d, new_lbl)

        self._config[d.value_key] = new_raw
        cfg.save(self._config)

        try:
            self.query_one(f"#opt-row-{d.key}", _OptionRow).update_value(new_lbl)
        except Exception:
            pass

        # Efeitos colaterais
        if d.value_key == "language":
            set_language(new_raw)
            for row_d in self._defs:
                try:
                    self.query_one(f"#opt-row-{row_d.key}", _OptionRow).refresh_label()
                except Exception:
                    pass
            self._update_description(self._sel_idx)
            self._refresh_tabbar()
            self.app.post_message(LanguageChanged())

        if d.value_key == "theme":
            # Aplica o tema nativo do Textual diretamente
            self.app.theme = new_raw

    def _refresh_tabbar(self) -> None:
        for num, key, i18n_key in self._TABS:
            try:
                lbl = self.query_one(f"#sw-tab-{key}", Label)
                active = key == self._active
                lbl.update(
                    f" [{num}{t(i18n_key)}] " if active else f"  {num}{t(i18n_key)}  "
                )
            except Exception:
                pass

    def action_tab_general(self) -> None:
        self._active = "general"

    def action_close(self) -> None:
        self.dismiss()
