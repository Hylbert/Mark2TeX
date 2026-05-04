import logging
import os
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

from .docker_manager import DockerManager
from .log_translator import log_translator
from .utils.visuals import M2TBannerWidget, M2TMenuOption
from .watcher import WatcherManager


# ── Logger configurado uma única vez ────────────────────────────────────────
def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("mark2tex")

    # Só ativa se DEBUG=1 ou MARK2TEX_DEBUG=1
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


class OptionItem(ListItem):
    def __init__(self, label_text: str, item_id: str | None = None) -> None:
        super().__init__(Label(label_text), id=item_id)
        self.label_text = label_text


class HelpScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window"):
            yield Label("AJUDA & ATALHOS", id="menu-header", classes="menu-header")
            with Vertical(id="help-content"):
                yield Label("Key Bindings:", id="help-bindings-title")
                yield Label("ESC / q      — Menu Global")
                yield Label("? / F1       — Abrir Ajuda")
                yield Label("c            — Compilar documento")
                yield Label("w            — Ativar/Desativar Watch Mode")
                yield Label("Tab          — Navegar entre painéis")
                yield Label("↑ ↓          — Navegar nas listas")
                yield Label("")
                yield Label("Fluxo:", id="help-commands-title")
                yield Label("1. Selecione um arquivo .md no painel esquerdo")
                yield Label("2. Escolha o template (tcc, artigo, projeto)")
                yield Label("3. Pressione c ou clique em COMPILAR")
                yield Label("4. Acompanhe o progresso no console abaixo")
                yield Label("")
                yield Label("Pressione ESC para voltar", id="help-footer")


class GlobalMenu(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-center"):
            with Vertical(classes="menu-window"):
                yield M2TBannerWidget()
                yield Label("─" * 46, id="menu-divider")
                yield ListView(
                    M2TMenuOption("AJUDA", item_id="opt-help"),
                    M2TMenuOption("SAIR", item_id="opt-exit"),
                    id="global-menu-list",
                )
                yield Label("ESC · fechar", id="menu-footer-hint")

    def on_mount(self) -> None:
        self.query_one("#global-menu-list", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "opt-help":
            self.app.push_screen(HelpScreen())
        elif event.item.id == "opt-exit":
            self.app.exit()


class Mark2TeXApp(App):
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.tcss")
    TITLE = "Mark2TeX Dashboard"

    BINDINGS = [
        ("escape", "show_global_menu", "Menu Global"),
        ("q", "show_global_menu", "Menu Global"),
        ("f1", "show_help_menu", "Ajuda"),
        ("question_mark", "show_help_menu", "Ajuda"),
        ("c", "compile_document", "Compilar"),
        ("w", "toggle_watch", "Watch Mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="outer-layout"):
            # ── Coluna esquerda: file explorer + config + console ──
            with Vertical(id="left-column"):
                with Horizontal(id="main-layout"):
                    with Vertical(id="file-explorer"):
                        yield ListView(id="file-list")

                    with Vertical(id="config-panel"):
                        with Vertical(id="status-panel"):
                            yield Label("Arquivo  : —", id="status-file")
                            yield Label("Template : —", id="status-template")

                        yield Label("Defina o Template do Arquivo PDF", id="template-title")
                        yield ListView(
                            OptionItem("tcc"),
                            OptionItem("artigo"),
                            OptionItem("projeto"),
                            id="template-list",
                        )

                        # Botões empilhados verticalmente para não sumirem
                        with Horizontal(id="action-bar"):
                            yield Button("COMPILAR", id="compile-btn")
                            yield Button("WATCH: OFF", id="watch-btn")

                yield ProgressBar(id="progress-bar", total=100)
                yield RichLog(id="console-panel", highlight=False, markup=False, wrap=True)

            with Vertical(id="preview-panel"):
                with ScrollableContainer(id="preview-scroll"):
                    yield Markdown("", id="preview-content")

        yield Footer()

    def on_mount(self) -> None:
        self.docker_manager = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching = False

        self.selected_file: str | None = None
        self.selected_template: str | None = None

        # ── Border titles ──
        self.query_one("#file-explorer").border_title = "• Arquivos"
        self.query_one("#config-panel").border_title = "• Configuração"
        self.query_one("#preview-panel").border_title = "• Preview"
        self.query_one("#console-panel").border_title = "• Console"

        md_files = sorted(f for f in os.listdir(".") if f.endswith(".md"))
        file_list = self.query_one("#file-list", ListView)
        for f in md_files:
            file_list.append(OptionItem(f))

    # ------------------------------------------------------------------
    # Eventos de lista
    # ------------------------------------------------------------------

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
        """Lê o arquivo .md e atualiza o widget Markdown de preview."""
        try:
            with open(filename, encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, PermissionError, OSError):
            content = f"_Não foi possível ler o arquivo `{filename}`._"

        preview = self.query_one("#preview-content", Markdown)
        self.call_after_refresh(preview.update, content)

    # ------------------------------------------------------------------
    # Actions / botões
    # ------------------------------------------------------------------

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

    def _log_console(self, message: str, style: str = "white") -> None:
        console = self.query_one("#console-panel", RichLog)
        console.write(Text(message, style=style))
        console.scroll_end()

    def _set_progress(self, value: int) -> None:
        self.query_one("#progress-bar", ProgressBar).update(progress=value)

    # ------------------------------------------------------------------
    # Watch Mode
    # ------------------------------------------------------------------

    def toggle_watch_mode(self) -> None:
        btn = self.query_one("#watch-btn", Button)

        if not self.is_watching:
            selected_file, selected_template = self._get_selection()
            if not selected_file or not selected_template:
                self._log_console(
                    "❌ Selecione um arquivo e um template antes de ativar o Watch Mode.",
                    style="#e05c5c",
                )
                return

            self.watcher_manager.start_watching(
                selected_file,
                selected_template,
                lambda: self.compile_specific_document(selected_file, selected_template),
            )
            self.is_watching = True
            btn.label = Text.assemble(
                ("● ", "bold rgb(76,175,135)"),
                ("WATCH: ON", "white bold"),
            )
            btn.add_class("watching")
            self._log_console(f"🔭 Watch Mode ativado para {selected_file}...", style="#5ab4bc")
        else:
            self.watcher_manager.stop_watching()
            self.is_watching = False
            btn.label = Text.assemble(
                ("● ", "rgb(120,120,120)"),
                ("WATCH: OFF", "white"),
            )
            btn.remove_class("watching")
            self._log_console("💤 Watch Mode desativado.", style="#e0a24a")

    # ------------------------------------------------------------------
    # Compilação
    # ------------------------------------------------------------------

    def compile_document(self) -> None:
        selected_file, selected_template = self._get_selection()
        if not selected_file or not selected_template:
            self._log_console(
                "❌ Selecione um arquivo e um template para compilar.", style="#e05c5c"
            )
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
        ui(
            "console",
            (f"🚀 Compilando {selected_file} com template '{selected_template}'...", "#5ab4bc"),
        )

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
            ui("console", (f"❌ Erro inesperado: {exc}", "#e05c5c"))

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
