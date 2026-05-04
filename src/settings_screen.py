from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static

from . import config as cfg
from .config import SUPPORTED_LANGUAGES
from .i18n import get_language, set_language, t
from .utils.visuals import M2TSettingsOption


# ---------------------------------------------------------------------------
# Tab bar item
# ---------------------------------------------------------------------------

class _TabItem(ListItem):
    def __init__(self, key: str, label: str) -> None:
        super().__init__(id=f"tab-{key}")
        self._key = key
        self._label = label

    def compose(self) -> ComposeResult:
        yield Static(self._label, id=f"tab-label-{self._key}", classes="settings-tab-label")

    def watch_highlighted(self, value: bool) -> None:
        try:
            s = self.query_one(f"#tab-label-{self._key}", Static)
            s.set_classes("settings-tab-label settings-tab-active" if value else "settings-tab-label")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# SettingsScreen — btop-style
# ---------------------------------------------------------------------------

class SettingsScreen(ModalScreen):
    """
    Tela de ajustes no estilo btop:
    - Borda com título
    - Abas no topo (Tab / Shift+Tab para navegar)
    - Conteúdo à direita, opções aplicadas imediatamente ao selecionar
    - ESC fecha e salva
    """

    BINDINGS = [
        Binding("escape", "close", "Fechar & Salvar"),
        Binding("tab", "next_tab", "Próxima aba", show=False),
        Binding("shift+tab", "prev_tab", "Aba anterior", show=False),
    ]

    # Abas disponíveis: (chave, i18n_key)
    _TABS = [
        ("language", "settings.tab_language"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._settings = cfg.load()
        self._active_tab = "language"

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-window"):
            # ── Cabeçalho / aba bar ──
            with Horizontal(id="settings-tab-bar"):
                yield Label(f" {t('settings.title')} ", id="settings-title-label")
                yield ListView(
                    *[_TabItem(key, f" {t(i18n_key)} ") for key, i18n_key in self._TABS],
                    id="settings-tabs",
                )
                yield Label(" ESC · fechar ", id="settings-esc-hint")

            # ── Corpo ──
            with Horizontal(id="settings-body"):
                # Painel de conteúdo da aba ativa
                with Vertical(id="settings-content"):
                    yield from self._build_tab(self._active_tab)

            # ── Rodapé ──
            yield Label(
                f" {t('settings.saved_at')} {cfg.CONFIG_FILE} ",
                id="settings-footer",
            )

    def _build_tab(self, tab: str):
        """Gera os widgets do conteúdo da aba selecionada."""
        if tab == "language":
            current = self._settings.get("language", get_language())
            yield Label(f" {t('settings.language')} ", classes="settings-section-title")
            yield ListView(
                *[
                    M2TSettingsOption(
                        label=name,
                        value=code,
                        selected=(code == current),
                    )
                    for code, name in SUPPORTED_LANGUAGES.items()
                ],
                id="language-list",
            )

    # ------------------------------------------------------------------
    # Tab navigation
    # ------------------------------------------------------------------

    def action_next_tab(self) -> None:
        keys = [k for k, _ in self._TABS]
        idx = keys.index(self._active_tab)
        self._switch_tab(keys[(idx + 1) % len(keys)])

    def action_prev_tab(self) -> None:
        keys = [k for k, _ in self._TABS]
        idx = keys.index(self._active_tab)
        self._switch_tab(keys[(idx - 1) % len(keys)])

    def _switch_tab(self, key: str) -> None:
        self._active_tab = key
        content = self.query_one("#settings-content", Vertical)
        content.remove_children()
        for w in self._build_tab(key):
            content.mount(w)

    # ------------------------------------------------------------------
    # Opções aplicadas imediatamente (sem botão salvar)
    # ------------------------------------------------------------------

    @on(ListView.Selected, "#language-list")
    def on_language_selected(self, event: ListView.Selected) -> None:
        new_lang = event.item.id.removeprefix("opt-")
        if new_lang == self._settings.get("language"):
            return

        # Atualiza visual dos itens
        for code in SUPPORTED_LANGUAGES:
            try:
                item = self.query_one(f"#opt-{code}", M2TSettingsOption)
                item.mark_selected(code == new_lang)
            except Exception:
                pass

        # Salva e aplica imediatamente
        self._settings["language"] = new_lang
        cfg.save(self._settings)
        set_language(new_lang)

        # Recarrega a interface inteira
        self.app.post_message(LanguageChanged())

    # ------------------------------------------------------------------
    # Fechar
    # ------------------------------------------------------------------

    def action_close(self) -> None:
        self.dismiss()

    def on_mount(self) -> None:
        # Foca a lista de conteúdo ao abrir
        try:
            self.query_one("#language-list", ListView).focus()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Mensagem para o app recarregar a UI
# ---------------------------------------------------------------------------

from textual.message import Message  # noqa: E402


class LanguageChanged(Message):
    """Postada quando o idioma é alterado nas settings. O app escuta e recarrega a UI."""
