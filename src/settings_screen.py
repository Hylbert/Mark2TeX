from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListView

from . import config as cfg
from .config import SUPPORTED_LANGUAGES
from .i18n import get_language, set_language, t
from .utils.visuals import M2TBannerWidget, M2TSettingsOption


class SettingsScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def __init__(self) -> None:
        super().__init__()
        self._settings = cfg.load()
        self._pending_lang = self._settings.get("language", get_language())

    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window"):
            yield M2TBannerWidget()
            yield Label("─" * 46, id="menu-divider")
            yield Label(t("settings.title"), id="menu-header", classes="menu-header")

            with Horizontal(id="settings-body"):
                # Coluna esquerda — categorias
                with Vertical(id="settings-categories"):
                    yield Label("🌐 " + t("settings.language"), classes="settings-cat-active")

                # Coluna direita — opções da categoria
                with Vertical(id="settings-options"):
                    yield Label(t("settings.language"), classes="settings-section-title")
                    yield ListView(
                        *[
                            M2TSettingsOption(
                                label=name,
                                value=code,
                                selected=(code == self._pending_lang),
                            )
                            for code, name in SUPPORTED_LANGUAGES.items()
                        ],
                        id="language-list",
                    )
                    yield Label(
                        f"{t('settings.saved_at')}\n{cfg.CONFIG_FILE}",
                        id="settings-path-hint",
                    )

            with Horizontal(id="settings-actions"):
                yield Button(t("settings.save"),   id="btn-save",   variant="primary")
                yield Button(t("settings.cancel"), id="btn-cancel")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "language-list":
            return
        new_lang = event.item.id.removeprefix("opt-")
        for code in SUPPORTED_LANGUAGES:
            item = self.query_one(f"#opt-{code}", M2TSettingsOption)
            item.mark_selected(code == new_lang)
        self._pending_lang = new_lang

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self._settings["language"] = self._pending_lang
            cfg.save(self._settings)
            set_language(self._pending_lang)
            self.dismiss(True)
        elif event.button.id == "btn-cancel":
            self.dismiss(False)
