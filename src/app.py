import os
import re
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Button, Static, ProgressBar, RichLog
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from docker_manager import DockerManager
from log_translator import LogTranslator
from watcher import WatcherManager
from utils.visuals import render_logo, render_icon

class HelpScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="menu-window"):
            yield Label(" 📖 AJUDA & ATALHOS ", id="menu-header", classes="menu-header")
            with Vertical(id="help-content"):
                yield Label("\nKey Bindings:", id="help-bindings-title")
                yield Label("ESC / q  - Menu Global")
                yield Label("F1 / h / ? - Abrir Ajuda")
                yield Label("\nCommands:", id="help-commands-title")
                yield Label("c / Compile - Compila arquivo selecionado")
                yield Label("w / Watch   - Auto-compilação")
                yield Label("\n")
                yield Label("Pressione ESC para voltar", id="help-footer")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

class GlobalMenu(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-center"):
            with Vertical(classes="menu-window"):
                logo_text = render_icon()
                yield Static(logo_text, id="global-menu-logo")

                yield ListView(
                    ListItem(Label("AJUDA"), id="opt-help"),
                    ListItem(Label("SAIR"), id="opt-exit"),
                    id="global-menu-list"
                )

    def on_mount(self) -> None:
        self.query_one("#global-menu-list", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_item = event.item
        if selected_item.id == "opt-help":
            self.app.push_screen(HelpScreen())
        elif selected_item.id == "opt-exit":
            self.app.exit()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

class Mark2TeXApp(App):
    CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.tcss")
    TITLE = "Mark2TeX Dashboard"
    BINDINGS = [
        ("escape", "show_global_menu", "Menu Global"),
        ("f1", "show_help_menu", "Ajuda"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-container"):
            with Horizontal(id="main-layout"):
                with Vertical(id="file-explorer"):
                    yield Label("📁 Markdown Files", id="explorer-title")
                    yield ListView(id="file-list")
                with Vertical(id="config-panel"):
                    with Vertical(id="welcome-panel"):
                        logo_text = render_logo()
                        yield Static(logo_text, id="welcome-logo", expand=True)
                        yield Label(
                            "📖 Guia Rápido:\n"
                            "1. Use as setas (← → ↑ ↓) ou (h j k l) para navegar\n"
                            "⌨️ Atalhos:\n"
                            "q / ESC - Menu de Saída\n"
                            "h / ? / F1 - Ajuda",
                            id="welcome-instructions"
                        )

                    yield Label("Select Template:")
                    yield ListView(
                        ListItem(Label("tcc")),
                        ListItem(Label("artigo")),
                        ListItem(Label("projeto")),
                        id="template-list"
                    )
                    yield Button("🚀 COMPILAR (c)", id="compile-btn")
                    yield Button("👀 MODO ASSISTIDO: OFF (w)", id="watch-btn")

            yield ProgressBar(id="progress-bar")
            yield RichLog(id="console-panel", highlight=False, markup=True)
        yield Footer()

    def on_key(self, event) -> None:
        key = event.key.lower() if hasattr(event.key, 'lower') else event.key

        if key == "q":
            self.action_show_global_menu()
            return
        elif key in ("h", "?"):
            self.action_show_global_menu()
            return
        elif key == "c":
            self.compile_document()
            return
        elif key == "w":
            self.toggle_watch_mode()
            return

        if key == "right" or key == "l":
            focused = self.screen.focused
            if focused and focused.id == "file-list":
                self.query_one("#template-list").focus()
            elif focused and focused.id == "template-list":
                self.query_one("#compile-btn").focus()
        elif key == "left" or key == "h":
            focused = self.screen.focused
            if focused and focused.id == "template-list":
                self.query_one("#file-list").focus()
            elif focused and (focused.id == "compile-btn" or focused.id == "watch-btn"):
                self.query_one("#template-list").focus()
        elif key == "down" or key == "j":
            focused = self.screen.focused
            if focused and focused.id == "template-list":
                list_view = self.query_one("#template-list", ListView)
                if list_view.highlighted_child and list_view.children and list_view.highlighted_child == list_view.children[-1]:
                    self.query_one("#compile-btn").focus()
            elif focused and focused.id == "compile-btn":
                self.query_one("#watch-btn").focus()
        elif key == "up" or key == "k":
            focused = self.screen.focused
            if focused and focused.id == "template-list":
                list_view = self.query_one("#template-list", ListView)
                if list_view.highlighted_child and list_view.children and list_view.highlighted_child == list_view.children[0]:
                    self.query_one("#file-list").focus()
            elif focused and focused.id == "watch-btn":
                self.query_one("#compile-btn").focus()

    def action_show_global_menu(self) -> None:
        self.push_screen(GlobalMenu())

    def action_show_help_menu(self) -> None:
        self.push_screen(HelpScreen())

    def on_mount(self) -> None:
        self.docker_manager = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching = False
        self._console_history = ""
        files = [f for f in os.listdir('.') if f.endswith('.md')]
        file_list = self.query_one("#file-list", ListView)
        for f in files:
            file_list.append(ListItem(Label(f)))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compile-btn":
            self.compile_document()
        elif event.button.id == "watch-btn":
            self.toggle_watch_mode()

    def toggle_watch_mode(self) -> None:
        btn = self.query_one("#watch-btn", Button)
        file_list = self.query_one("#file-list", ListView)
        template_list = self.query_one("#template-list", ListView)

        if not self.is_watching:
            selected_file = None
            if file_list.highlighted_child:
                selected_file = str(file_list.highlighted_child.query_one(Label).renderable)

            selected_template = None
            if template_list.highlighted_child:
                selected_template = str(template_list.highlighted_child.query_one(Label).renderable)

            if not selected_file or not selected_template:
                self.query_one("#console-panel", RichLog).update("❌ Select file and template first to enable Watch Mode.")
                return

            self.watcher_manager.start_watching(
                selected_file,
                selected_template,
                lambda: self.compile_specific_document(selected_file, selected_template)
            )
            self.is_watching = True
            btn.label = "👀 Watch Mode: ON"
            self.query_one("#console-panel", RichLog).write(f"🔭 Watch Mode enabled for {selected_file}...")
        else:
            self.watcher_manager.stop_watching()
            self.is_watching = False
            btn.label = "👀 Watch Mode: OFF"
            self.query_one("#console-panel", RichLog).write("💤 Watch Mode disabled.")

    def compile_document(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        template_list = self.query_one("#template-list", ListView)

        selected_file = None
        if file_list.highlighted_child:
            selected_file = str(file_list.highlighted_child.query_one(Label).renderable)

        selected_template = None
        if template_list.highlighted_child:
            selected_template = str(template_list.highlighted_child.query_one(Label).renderable)

        if not selected_file or not selected_template:
            self.query_one("#console-panel", RichLog).write("❌ Please select both a file and a template.")
            return

        self.compile_specific_document(selected_file, selected_template)

    def compile_specific_document(self, selected_file: str, selected_template: str) -> None:
        """Dispara a compilação de um arquivo e template específicos."""
        self.run_worker(lambda: self._run_compilation(selected_file, selected_template), thread=True)

    def _run_compilation(self, selected_file: str, selected_template: str) -> None:
        """Lógica de compilação que roda em background."""
        with open("tui_debug.log", "a", encoding="utf-8") as f:
            f.write(f"DEBUG: Starting compilation for {selected_file}...\n")

        def update_ui(action, value):
            """Helper para atualizar a UI com segurança a partir de qualquer thread."""
            with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                f.write(f"UI REQUEST - {action}: {value}\n")

            self.call_from_thread(self._apply_ui_update, action, value)

        update_ui("progress", 0)
        update_ui("console", f"🚀 Compiling {selected_file} with {selected_template}...\n")



        try:
            for line in self.docker_manager.compile(selected_file, selected_template):
                # Sanitização: ignoramos linhas vazias ou apenas com espaços para evitar inundação de eventos
                clean_line = line.strip()
                if not clean_line:
                    continue

                # Log RAW para depuração total
                with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"RAW LINE: {line}")

                # 1. Verificação de Progresso Real
                progress_match = re.search(r"PROGRESS:(\d+)%", clean_line)
                if progress_match:
                    percent = int(progress_match.group(1))
                    update_ui("progress", percent / 100)

                # 2. Simulação de Atividade
                if "latexmk" in clean_line or "Warning" in clean_line or "Page" in clean_line:
                    update_ui("progress_activity", True)

                # 3. Tradução e Filtragem
                translated_line = LogTranslator.translate(clean_line)
                if translated_line:
                    update_ui("console", translated_line)
        except Exception as e:
            update_ui("console", f"❌ Unexpected error: {str(e)}")

    def _apply_ui_update(self, action: str, value) -> None:
        """Aplica a atualização na UI. Executado sempre na Main Thread."""
        with open("tui_console_debug.log", "a", encoding="utf-8") as f:
            f.write(f"UI APPLY - {action}: {value}\n")
        try:
            if action == "progress":
                widgets = self.query("#progress-bar", ProgressBar)
                if widgets:
                    bar = widgets.first()
                    bar.progress = value
                    bar.refresh()
            elif action == "progress_activity":
                widgets = self.query("#progress-bar", ProgressBar)
                if widgets:
                    bar = widgets.first()
                    if bar.progress < 1.0:
                        bar.progress = min(bar.progress + 0.005, 0.99)
                        bar.refresh()
            elif action == "console":
                # DEBUG: Verifica se o widget existe
                with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"WIDGET CHECK - Searching for #console-panel...\n")

                console = self.query_one("#console-panel", RichLog)

                with open("tui_console_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"WIDGET FOUND - writing value: {value}\n")

                colored_value = f"[white]{value}[/white]"
                console.write(colored_value)
                console.scroll_end(flush=True)

                self.refresh()
        except Exception as e:
            # Logamos o erro no terminal do sistema para depuração, mas não crashamos o app
            print(f"UI Update Error ({action}): {e}")


if __name__ == "__main__":
    app = Mark2TeXApp()
    app.run()
