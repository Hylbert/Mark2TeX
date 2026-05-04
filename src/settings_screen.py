from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static

from . import config as cfg
from .config import SUPPORTED_LANGUAGES
from .i18n import get_language, set_language, t


# ---------------------------------------------------------------------------
# Mensagem pública — o app escuta e atualiza os labels
# ---------------------------------------------------------------------------

class LanguageChanged(Message):
    """Postada quando o idioma é alterado. O app escuta e recarrega a UI."""


# ---------------------------------------------------------------------------
# Estrutura de uma opção de settings
# ---------------------------------------------------------------------------

@dataclass
class _SettingDef:
    key: str           # chave interna
    label: str         # texto exibido na coluna esquerda
    description: str   # texto exibido na coluna direita
    choices: list[Any] # lista de valores possíveis
    value_key: str     # chave no dict de config


def _build_settings_defs() -> list[_SettingDef]:
    """Constrói as definições de opções com base no idioma atual."""
    lang_names = list(SUPPORTED_LANGUAGES.values())
    return [
        _SettingDef(
            key="language",
            label=t("settings.opt_language"),
            description=t("settings.desc_language"),
            choices=lang_names,
            value_key="language",
        ),
    ]


# ---------------------------------------------------------------------------
# Widget de item da lista de opções (coluna esquerda)
# ---------------------------------------------------------------------------

class _OptionItem(ListItem):
    """Item da lista de opções: nome em bold + valor atual abaixo."""

    def __init__(self, definition: _SettingDef, current_value_label: str) -> None:
        super().__init__(id=f"setting-{definition.key}")
        self._def = definition
        self._value_label = current_value_label

    def compose(self) -> ComposeResult:
        yield Static(self._def.label, classes="opt-name")
        yield Static(self._value_label, id=f"val-{self._def.key}", classes="opt-value")

    def update_value(self, new_label: str) -> None:
        self._value_label = new_label
        try:
            self.query_one(f"#val-{self._def.key}", Static).update(new_label)
        except Exception:
            pass

    def watch_highlighted(self, value: bool) -> None:
        try:
            name = self.query_one(".opt-name", Static)
            val  = self.query_one(".opt-value", Static)
            if value:
                name.set_classes("opt-name opt-name-hl")
                val.set_classes("opt-value opt-value-hl")
            else:
                name.set_classes("opt-name")
                val.set_classes("opt-value")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# SettingsScreen
# ---------------------------------------------------------------------------

class SettingsScreen(ModalScreen):
    """
    Tela de ajustes com layout de duas colunas:
    - Esquerda: lista de opções (nome em bold + valor atual)
    - Direita: descrição da opção selecionada + controle de valor
    Abas numeradas no topo para futuras categorias.
    Alterações são aplicadas e salvas imediatamente.
    """

    BINDINGS = [
        Binding("escape", "close", "Fechar"),
        Binding("left",  "prev_value", "Valor anterior", show=False),
        Binding("right", "next_value", "Próximo valor",  show=False),
        Binding("1",     "tab_general", show=False),
    ]

    # Abas: (número, chave, i18n_key) — fácil de expandir
    _TABS: list[tuple[str, str, str]] = [
        ("1", "general", "settings.tab_general"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._config   = cfg.load()
        self._active   = "general"
        self._defs     = _build_settings_defs()
        self._sel_idx  = 0          # índice da opção selecionada

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Vertical(id="sw-window"):
            # ── Linha de abas ──
            with Horizontal(id="sw-tabbar"):
                yield Label(" tab→ ", id="sw-tab-hint")
                for num, key, i18n_key in self._TABS:
                    active_cls = " sw-tab-active" if key == self._active else ""
                    yield Label(
                        f" [{num}{t(i18n_key)}] " if key == self._active
                        else f"  {num}{t(i18n_key)}  ",
                        id=f"sw-tab-{key}",
                        classes=f"sw-tab{active_cls}",
                    )

            # ── Corpo ──
            with Horizontal(id="sw-body"):
                # Coluna esquerda — lista de opções
                with Vertical(id="sw-left"):
                    yield ListView(
                        *self._build_option_items(),
                        id="sw-option-list",
                    )

                # Divisor vertical
                yield Static(" ", id="sw-divider")

                # Coluna direita — descrição + controle
                with Vertical(id="sw-right"):
                    yield Static("", id="sw-description")
                    yield Static("", id="sw-control")

            # ── Rodapé ──
            yield Label(
                f" {t('settings.saved_at')} {cfg.CONFIG_FILE} ",
                id="sw-footer",
            )

    def _build_option_items(self) -> list[_OptionItem]:
        items = []
        for d in self._defs:
            raw = self._config.get(d.value_key, "")
            items.append(_OptionItem(d, self._raw_to_label(d, raw)))
        return items

    def _raw_to_label(self, d: _SettingDef, raw: str) -> str:
        """Converte o valor interno (ex: 'pt_BR') para rótulo exibido (ex: 'Português (Brasil)')."""
        if d.value_key == "language":
            return SUPPORTED_LANGUAGES.get(raw, raw)
        return str(raw)

    def _label_to_raw(self, d: _SettingDef, label: str) -> str:
        """Converte rótulo exibido de volta ao valor interno."""
        if d.value_key == "language":
            for code, name in SUPPORTED_LANGUAGES.items():
                if name == label:
                    return code
        return label

    # ------------------------------------------------------------------
    # on_mount — selecionada a primeira opção por padrão
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        lv = self.query_one("#sw-option-list", ListView)
        lv.focus()
        self._update_right_panel(0)

    # ------------------------------------------------------------------
    # Painel direito: descrição + controle de valor
    # ------------------------------------------------------------------

    def _update_right_panel(self, idx: int) -> None:
        if not self._defs:
            return
        self._sel_idx = idx
        d   = self._defs[idx]
        raw = self._config.get(d.value_key, "")
        cur = self._raw_to_label(d, raw)

        # Descrição
        self.query_one("#sw-description", Static).update(d.description)

        # Controle: ← valor →
        choices = d.choices
        cur_i   = choices.index(cur) if cur in choices else 0
        prev_v  = choices[(cur_i - 1) % len(choices)]
        next_v  = choices[(cur_i + 1) % len(choices)]
        ctrl = (
            f"\n←  [dim]{prev_v}[/dim]   "
            f"[bold white]{cur}[/bold white]   "
            f"[dim]{next_v}[/dim]  →"
        )
        self.query_one("#sw-control", Static).update(ctrl)

    # ------------------------------------------------------------------
    # Navegação na lista — atualiza painel direito ao mover
    # ------------------------------------------------------------------

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id != "sw-option-list":
            return
        if event.item is None:
            return
        key = event.item.id.removeprefix("setting-")
        idx = next((i for i, d in enumerate(self._defs) if d.key == key), 0)
        self._update_right_panel(idx)

    # ------------------------------------------------------------------
    # ← → para ciclar o valor da opção selecionada
    # ------------------------------------------------------------------

    def action_prev_value(self) -> None:
        self._cycle_value(-1)

    def action_next_value(self) -> None:
        self._cycle_value(1)

    def _cycle_value(self, direction: int) -> None:
        if not self._defs:
            return
        d       = self._defs[self._sel_idx]
        raw     = self._config.get(d.value_key, "")
        cur     = self._raw_to_label(d, raw)
        choices = d.choices
        cur_i   = choices.index(cur) if cur in choices else 0
        new_lbl = choices[(cur_i + direction) % len(choices)]
        new_raw = self._label_to_raw(d, new_lbl)

        # Persiste
        self._config[d.value_key] = new_raw
        cfg.save(self._config)

        # Atualiza item na lista esquerda
        try:
            item = self.query_one(f"#setting-{d.key}", _OptionItem)
            item.update_value(new_lbl)
        except Exception:
            pass

        # Atualiza painel direito
        self._update_right_panel(self._sel_idx)

        # Efeitos colaterais por tipo de opção
        if d.value_key == "language":
            set_language(new_raw)
            self.app.post_message(LanguageChanged())

    # ------------------------------------------------------------------
    # Enter também avança o valor (como no btop)
    # ------------------------------------------------------------------

    @on(ListView.Selected, "#sw-option-list")
    def on_option_enter(self, _: ListView.Selected) -> None:
        self._cycle_value(1)

    # ------------------------------------------------------------------
    # Aba general (binding "1")
    # ------------------------------------------------------------------

    def action_tab_general(self) -> None:
        self._active = "general"
        # Futuramente recarrega o conteúdo da aba

    # ------------------------------------------------------------------
    # Fechar
    # ------------------------------------------------------------------

    def action_close(self) -> None:
        self.dismiss()
