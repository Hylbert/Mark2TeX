import os

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button, Footer, Header, Label,
    ListItem, ListView, ProgressBar, RichLog, Static,
)

from docker_manager import DockerManager
from log_translator import log_translator
from watcher import WatcherManager
from utils.visuals import render_logo, render_icon

class HelpScreen(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window"):
            yield Label("📖 AJUDA & ATALHOS", id="menu-header", classes="menu-header")
            with Vertical(id="help-content"):
                yield Label("Key Bindings:", id="help-bindings-title")
                yield Label("ESC / q  — Menu Global")
                yield Label("F1 / ?   — Abrir Ajuda")
                yield Label("")
                yield Label("Commands:", id="help-commands-title")
                yield Label("c  — Compila arquivo selecionado")
                yield Label("w  — Ativa/Desativa Watch Mode")
                yield Label("")
                yield Label("Pressione ESC para voltar", id="help-footer")


class GlobalMenu(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Fechar")]

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-center"):
            with Vertical(classes="menu-window"):
                yield Static(render_icon(), id="global-menu-logo")
                yield ListView(
                    ListItem(Label("AJUDA"), id="opt-help"),
                    ListItem(Label("SAIR"),  id="opt-exit"),
                    id="global-menu-list",
                )

    def on_mount(self) -> None:
        self.query_one("#global-menu-list", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "opt-help":
            self.app.push_screen(HelpScreen())
        elif event.item.id == "opt-exit":
            self.app.exit()


class Mark2TeXApp(App):
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.tcss")
    TITLE    = "Mark2TeX Dashboard"

    BINDINGS = [
        ("escape",         "show_global_menu", "Menu Global"),
        ("q",              "show_global_menu", "Menu Global"),
        ("f1",             "show_help_menu",   "Ajuda"),
        ("question_mark",  "show_help_menu",   "Ajuda"),
        ("c",              "compile_document", "Compilar"),
        ("w",              "toggle_watch",     "Watch Mode"),
    ]

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-container"):
            with Horizontal(id="main-layout"):

                with Vertical(id="file-explorer"):
                    yield Label("📁 Markdown Files", id="explorer-title")
                    yield ListView(id="file-list")

                with Vertical(id="config-panel"):
                    with Vertical(id="welcome-panel"):
                        yield Static(render_logo(), id="welcome-logo", expand=True)
                        yield Label(
                            "📖 Guia Rápido:\n"
                            "  Use Tab / Shift+Tab para navegar entre painéis\n"
                            "  Use ↑ ↓ para navegar nas listas\n\n"
                            "⌨️  Atalhos:\n"
                            "  q / ESC  — Menu Global\n"
                            "  ? / F1   — Ajuda\n"
                            "  c        — Compilar\n"
                            "  w        — Watch Mode",
                            id="welcome-instructions",
                        )

                    yield Label("Select Template:")
                    yield ListView(
                        ListItem(Label("tcc")),
                        ListItem(Label("artigo")),
                        ListItem(Label("projeto")),
                        id="template-list",
                    )
                    yield Button("🚀 COMPILAR", id="compile-btn")
                    yield Button("👀 MODO ASSISTIDO: OFF", id="watch-btn")

            yield ProgressBar(id="progress-bar", total=100)
            yield RichLog(id="console-panel", highlight=False, markup=False, wrap=True)
        yield Footer()

    # ── Mount ─────────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self.docker_manager  = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching     = False

        file_list = self.query_one("#file-list", ListView)
        for f in sorted(f for f in os.listdir(".") if f.endswith(".md")):
            file_list.append(ListItem(Label(f)))

    # ── Actions (BINDINGS) ────────────────────────────────────────────────────

    def action_show_global_menu(self) -> None:
        self.push_screen(GlobalMenu())

    def action_show_help_menu(self) -> None:
        self.push_screen(HelpScreen())

    def action_compile_document(self) -> None:
        self.compile_document()

    def action_toggle_watch(self) -> None:
        self.toggle_watch_mode()

    # ── Botões ────────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compile-btn":
            self.compile_document()
        elif event.button.id == "watch-btn":
            self.toggle_watch_mode()

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    def _get_selection(self) -> tuple[str | None, str | None]:
        """Retorna (arquivo_selecionado, template_selecionado)."""
        file_list     = self.query_one("#file-list",     ListView)
        template_list = self.query_one("#template-list", ListView)

        selected_file = (
            str(file_list.highlighted_child.query_one(Label).renderable)
            if file_list.highlighted_child else None
        )
        selected_template = (
            str(template_list.highlighted_child.query_one(Label).renderable)
            if template_list.highlighted_child else None
        )
        return selected_file, selected_template

    def _log(self, message: str, style: str = "white") -> None:
        """Escreve uma linha no console com estilo Rich."""
        console = self.query_one("#console-panel", RichLog)
        console.write(Text(message, style=style))
        console.scroll_end()

    def _set_progress(self, value: int) -> None:
        """Atualiza a barra de progresso (0–100)."""
        self.query_one("#progress-bar", ProgressBar).update(progress=value)

    # ── Watch Mode ────────────────────────────────────────────────────────────

    def toggle_watch_mode(self) -> None:
        btn = self.query_one("#watch-btn", Button)

        if not self.is_watching:
            selected_file, selected_template = self._get_selection()
            if not selected_file or not selected_template:
                self._log("❌ Selecione um arquivo e um template antes de ativar o Watch Mode.", style="red")
                return

            self.watcher_manager.start_watching(
                selected_file,
                selected_template,
                lambda: self.compile_specific_document(selected_file, selected_template),
            )
            self.is_watching = True
            btn.label = "👀 MODO ASSISTIDO: ON"
            self._log(f"🔭 Watch Mode ativado para {selected_file}...", style="cyan")
        else:
            self.watcher_manager.stop_watching()
            self.is_watching = False
            btn.label = "👀 MODO ASSISTIDO: OFF"
            self._log("💤 Watch Mode desativado.", style="yellow")

    # ── Compilação ────────────────────────────────────────────────────────────

    def compile_document(self) -> None:
        selected_file, selected_template = self._get_selection()
        if not selected_file or not selected_template:
            self._log("❌ Selecione um arquivo e um template para compilar.", style="red")
            return
        self.compile_specific_document(selected_file, selected_template)

    def compile_specific_document(self, selected_file: str, selected_template: str) -> None:
        """Dispara a compilação em background thread."""
        self.run_worker(
            lambda: self._run_compilation(selected_file, selected_template),
            thread=True,
        )

    def _run_compilation(self, selected_file: str, selected_template: str) -> None:
        """Roda em background thread — nunca acessa widgets diretamente."""

        def ui(action: str, value=None) -> None:
            with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                f.write(f"UI REQUEST - {action}: {value}\n")
            self.call_from_thread(self._apply_ui_update, action, value)

        ui("progress", 0)
        ui("console", (f"🚀 Compilando {selected_file} com template \'{selected_template}\'...", "cyan"))

        try:
            for line in self.docker_manager.compile(selected_file, selected_template):
                clean = line.strip()
                if not clean:
                    continue

                with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"RAW LINE: {line}")

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
            ui("console", (f"❌ Erro inesperado: {exc}", "red"))

    # ── Aplicador de UI  ───────────────────────────────

    def _apply_ui_update(self, action: str, value=None) -> None:
        """Executado sempre na Main Thread via call_from_thread."""
        with open("tui_console_debug.log", "a", encoding="utf-8") as f:
            f.write(f"UI APPLY - {action}: {value}\n")
        try:
            if action == "progress":
                self._set_progress(int(value))

            elif action == "progress_bump":
                bar     = self.query_one("#progress-bar", ProgressBar)
                current = bar.progress or 0
                if current < 99:
                    self._set_progress(min(int(current) + 1, 99))

            elif action == "console":
                message, style = value
                self._log(message, style=style)

        except Exception as exc:
            print(f"[UI Error] {action}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    Mark2TeXApp().run()