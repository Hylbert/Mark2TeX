"""Modal screen shown when a selected .md has no YAML frontmatter."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical, Horizontal

from .i18n import t


class YamlInjectScreen(ModalScreen):
    """Confirmation modal before injecting YAML frontmatter into a .md file."""

    BINDINGS = [("escape", "dismiss_cancel", "Cancel")]

    def __init__(self, filename: str, template: str) -> None:
        super().__init__()
        self._filename = filename
        self._template = template

    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window", id="yaml-inject-window"):
            yield Label(t("yaml.title"), id="menu-header", classes="menu-header")
            yield Label(
                t("yaml.body").format(filename=self._filename, template=self._template),
                id="yaml-body",
            )
            yield Label(t("yaml.hint_restore"), id="yaml-hint")
            with Horizontal(id="yaml-btn-row"):
                yield Button(t("yaml.btn_inject"),  id="yaml-btn-inject",  variant="primary")
                yield Button(t("yaml.btn_cancel"),  id="yaml-btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#yaml-btn-inject", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yaml-btn-inject":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_dismiss_cancel(self) -> None:
        self.dismiss(False)
