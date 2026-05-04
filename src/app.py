import logging
import os
import shutil
import subprocess
from pathlib import Path

from platformdirs import user_log_dir
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Markdown,
    ProgressBar,
    RichLog,
)

from . import config as cfg
from .docker_manager import DockerManager
from .i18n import set_language, t
from .log_translator import log_translator
from .settings_screen import LanguageChanged, SettingsScreen
from .utils.visuals import M2TBannerWidget, M2TMenuOption
from .watcher import WatcherManager


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("mark2tex")
    if not (os.getenv("MARK2TEX_DEBUG") or os.getenv("DEBUG")):
        logger.addHandler(logging.NullHandler())
        return logger
    log_dir = Path(user_log_dir("mark2tex", appauthor=False))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "debug.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


_logger = _setup_logger()


def _copy_to_clipboard(text: str) -> None:
    """Copia texto para a área de transferência.

    Tenta, em ordem:
      1. pyperclip  (cross-platform, requer xclip/xsel/wl-clipboard no Linux)
      2. wl-copy    (Wayland nativo)
      3. xclip      (X11)
      4. xsel       (X11 alternativo)
    Lança RuntimeError se nenhum método funcionar.
    """
    # 1. pyperclip
    try:
        import pyperclip
        pyperclip.copy(text)
        return
    except Exception:
        pass

    # 2-4. ferramentas de sistema
    for cmd in (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=text.encode(), check=True, timeout=3)
                return
            except Exception:
                continue

    raise RuntimeError(
        "Nenhum mecanismo de clipboard disponível.\n"
        "Instale: xclip, xsel ou wl-clipboard (Wayland)."
    )


class OptionItem(ListItem):
    def __init__(self, label_text: str, item_id: str | None = None) -> None:
        super().__init__(Label(label_text), id=item_id)
        self.label_text = label_text


class HelpScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window"):
            yield Label(t("help.title"), id="menu-header", classes="menu-header")
            with Vertical(id="help-content"):
                yield Label(t("help.bindings_title"), id="help-bindings-title")
                yield Label("ESC / q      — " + t("menu.settings").capitalize() + " / " + t("menu.exit").lower())
                yield Label("? / F1       — " + t("menu.help").capitalize())
                yield Label("c            — " + t("btn.compile").capitalize())
                yield Label("w            — " + t("btn.watch_on") + " / " + t("btn.watch_off"))
                yield Label("Tab          — " + ("Navegar entre painéis" if t("menu.exit") == "SAIR" else "Navigate between panels"))
                yield Label("↑ ↓          — " + ("Navegar nas listas" if t("menu.exit") == "SAIR" else "Navigate lists"))
                yield Label("")
                yield Label(t("help.flow_title"), id="help-commands-title")
                yield Label(t("help.flow_1"))
                yield Label(t("help.flow_2"))
                yield Label(t("help.flow_3"))
                yield Label(t("help.flow_4"))
                yield Label("")
                yield Label(t("help.footer"), id="help-footer")


class GlobalMenu(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-center"):
            with Vertical(classes="menu-window"):
                yield M2TBannerWidget()
                yield Label("─" * 46, id="menu-divider")
                yield ListView(
                    M2TMenuOption(t("menu.settings"), item_id="opt-settings"),
                    M2TMenuOption(t("menu.help"),     item_id="opt-help"),
                    M2TMenuOption(t("menu.exit"),     item_id="opt-exit"),
                    id="global-menu-list",
                )
                yield Label("ESC · fechar", id="menu-footer-hint")

    def on_mount(self) -> None:
        self.query_one("#global-menu-list", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "opt-settings":
            self.app.push_screen(SettingsScreen())
        elif event.item.id == "opt-help":
            self.app.push_screen(HelpScreen())
        elif event.item.id == "opt-exit":
            self.app.exit()


class Mark2TeXApp(App):
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.tcss")
    TITLE = "Mark2TeX Dashboard"

    BINDINGS = [
        ("escape", "show_global_menu", "Menu Global"),
        ("q",      "show_global_menu", "Menu Global"),
        ("f1",     "show_help_menu",   "Ajuda"),
        ("question_mark", "show_help_menu", "Ajuda"),
        ("c",      "compile_document", "Compilar"),
        ("w",      "toggle_watch",     "Watch Mode"),
    ]

    def on_load(self) -> None:
        settings = cfg.load()
        set_language(settings.get("language", "pt_BR"))
        saved_theme = settings.get("theme", "textual-dark")
        self.theme = saved_theme

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="outer-layout"):
            with Vertical(id="left-column"):
                with Horizontal(id="main-layout"):
                    with Vertical(id="file-explorer"):
                        yield ListView(id="file-list")
                    with Vertical(id="config-panel"):
                        with Vertical(id="status-panel"):
                            yield Label(t("status.file"),     id="status-file")
                            yield Label(t("status.template"), id="status-template")
                        yield Label(t("panel.template_label"), id="template-title")
                        yield ListView(id="template-list")
                        with Horizontal(id="action-bar"):
                            yield Button(t("btn.compile"),   id="compile-btn")
                            yield Button(t("btn.watch_off"), id="watch-btn")
                yield ProgressBar(id="progress-bar", total=100)
                with Horizontal(id="console-bar"):
                    yield Button("⧉", id="copy-console-btn", classes="console-action-btn")
                yield RichLog(id="console-panel", highlight=False, markup=False, wrap=True)
            with Vertical(id="preview-panel"):
                with ScrollableContainer(id="preview-scroll"):
                    yield Markdown("", id="preview-content")
        yield Footer()

    def on_mount(self) -> None:
        self.docker_manager  = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching      = False
        self.selected_file:     str | None = None
        self.selected_template: str | None = None
        self._console_lines:    list[str]  = []
        self._refresh_ui_labels()
        self._populate_templates()
        self._populate_files()

    def _populate_templates(self) -> None:
        template_list = self.query_one("#template-list", ListView)
        template_list.clear()
        for name in self.docker_manager.list_templates():
            template_list.append(OptionItem(name))

    def _populate_files(self) -> None:
        md_files = sorted(f for f in os.listdir(".") if f.endswith(".md"))
        file_list = self.query_one("#file-list", ListView)
        for f in md_files:
            file_list.append(OptionItem(f))

    def _refresh_ui_labels(self) -> None:
        self.query_one("#file-explorer").border_title  = t("panel.files")
        self.query_one("#config-panel").border_title   = t("panel.config")
        self.query_one("#preview-panel").border_title  = t("panel.preview")
        self.query_one("#console-panel").border_title  = t("panel.console")
        self.query_one("#template-title",  Label).update(t("panel.template_label"))
        self.query_one("#status-file",     Label).update(t("status.file"))
        self.query_one("#status-template", Label).update(t("status.template"))
        self.query_one("#compile-btn",     Button).label = t("btn.compile")
        if not self.is_watching:
            self.query_one("#watch-btn", Button).label = t("btn.watch_off")

    def on_language_changed(self, _: LanguageChanged) -> None:
        self._refresh_ui_labels()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, OptionItem):
            return
        if event.list_view.id == "file-list":
            self.selected_file = item.label_text
            self.query_one("#status-file", Label).update(f"Arquivo  : {self.selected_file}")
        elif event.list_view.id == "template-list":
            self.selected_template = item.label_text
            self.query_one("#status-template", Label).update(f"Template : {self.selected_template}")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if not isinstance(item, OptionItem):
            return
        if event.list_view.id == "file-list":
            self.selected_file = item.label_text
            self.query_one("#status-file", Label).update(f"Arquivo  : {self.selected_file}")
            self._update_preview(item.label_text)
        elif event.list_view.id == "template-list":
            self.selected_template = item.label_text
            self.query_one("#status-template", Label).update(f"Template : {self.selected_template}")

    def _update_preview(self, filename: str) -> None:
        try:
            with open(filename, encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, PermissionError, OSError):
            content = f"_Não foi possível ler o arquivo `{filename}`._"
        preview = self.query_one("#preview-content", Markdown)
        self.call_after_refresh(preview.update, content)

    def _get_selection(self) -> tuple[str | None, str | None]:
        return self.selected_file, self.selected_template

    def action_show_global_menu(self) -> None:
        self.push_screen(GlobalMenu())

    def action_show_help_menu(self) -> None:
        self.push_screen(HelpScreen())

    def action_compile_document(self) -> None:
        self.compile_document()

    def action_toggle_watch(self) -> None:
        self.toggle_watch_mode()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compile-btn":
            self.compile_document()
        elif event.button.id == "watch-btn":
            self.toggle_watch_mode()
        elif event.button.id == "copy-console-btn":
            self._copy_console()

    def _copy_console(self) -> None:
        text = "\n".join(self._console_lines).strip()
        try:
            _copy_to_clipboard(text)
            btn = self.query_one("#copy-console-btn", Button)
            btn.label = "✓"
            btn.add_class("console-action-btn--copied")
            self.set_timer(1.5, self._reset_copy_btn)
        except RuntimeError as exc:
            self._log_console(f"❌ {exc}", style="#e05c5c")

    def _reset_copy_btn(self) -> None:
        btn = self.query_one("#copy-console-btn", Button)
        btn.label = "⧉"
        btn.remove_class("console-action-btn--copied")

    def _log_console(self, message: str, style: str = "white") -> None:
        self._console_lines.append(message)
        console = self.query_one("#console-panel", RichLog)
        console.write(Text(message, style=style))
        console.scroll_end()

    def _set_progress(self, value: int) -> None:
        self.query_one("#progress-bar", ProgressBar).update(progress=value)

    def toggle_watch_mode(self) -> None:
        btn = self.query_one("#watch-btn", Button)
        if not self.is_watching:
            selected_file, selected_template = self._get_selection()
            if not selected_file or not selected_template:
                self._log_console(t("compile.select_watch"), style="#e05c5c")
                return
            self.watcher_manager.start_watching(
                selected_file,
                selected_template,
                lambda: self.compile_specific_document(selected_file, selected_template),
            )
            self.is_watching = True
            btn.label = Text.assemble(("● ", "bold rgb(76,175,135)"), (t("btn.watch_on"), "white bold"))
            btn.add_class("watching")
            self._log_console(f"{t('watch.on')} {selected_file}...", style="#5ab4bc")
        else:
            self.watcher_manager.stop_watching()
            self.is_watching = False
            btn.label = Text.assemble(("● ", "rgb(120,120,120)"), (t("btn.watch_off"), "white"))
            btn.remove_class("watching")
            self._log_console(t("watch.off"), style="#e0a24a")

    def compile_document(self) -> None:
        selected_file, selected_template = self._get_selection()
        if not selected_file or not selected_template:
            self._log_console(t("compile.select_file"), style="#e05c5c")
            return
        self.compile_specific_document(selected_file, selected_template)

    def compile_specific_document(self, selected_file: str, selected_template: str) -> None:
        self.run_worker(
            lambda: self._run_compilation(selected_file, selected_template),
            thread=True,
        )

    def _run_compilation(self, selected_file: str, selected_template: str) -> None:
        def ui(action: str, value=None) -> None:
            _logger.debug("UI REQUEST - %s: %s", action, value)
            self.call_from_thread(self._apply_ui_update, action, value)

        ui("progress", 0)
        ui("console", (f"{t('compile.start')} {selected_file} com template '{selected_template}'...", "#5ab4bc"))
        try:
            for line in self.docker_manager.compile(selected_file, selected_template):
                clean = line.strip()
                if not clean:
                    continue
                _logger.debug("RAW LINE: %s", line)
                result = log_translator(clean)
                if result is None:
                    continue
                if result.startswith("__PROGRESS__"):
                    percent = int(result.removeprefix("__PROGRESS__"))
                    ui("progress", percent)
                    ui("console", (f"⏳ Processing... {percent}%", "white"))
                    continue
                if result.startswith(("⚠️", "⚠", "❌", "🔄")):
                    ui("progress_bump", None)
                ui("console", (result, "white"))
        except Exception as exc:
            ui("console", (f"{t('compile.error')}: {exc}", "#e05c5c"))

    def _apply_ui_update(self, action: str, value=None) -> None:
        _logger.debug("UI APPLY - %s: %s", action, value)
        try:
            if action == "progress":
                self._set_progress(int(value))
            elif action == "progress_bump":
                bar = self.query_one("#progress-bar", ProgressBar)
                current = bar.progress or 0
                if current < 99:
                    self._set_progress(min(int(current) + 1, 99))
            elif action == "console":
                message, style = value
                self._log_console(message, style=style)
        except Exception as exc:
            print(f"[UI Error] {action}: {exc}")


if __name__ == "__main__":
    Mark2TeXApp().run()
