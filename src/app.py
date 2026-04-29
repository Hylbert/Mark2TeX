import os
import re
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Button, Static, ProgressBar
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from docker_manager import DockerManager
from log_translator import LogTranslator
from watcher import WatcherManager
from logo_renderer import render_logo_to_text

# No more LOGO constant here

class ExitMenu(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="exit-menu-container"):
            yield Label(" MENU ", id="menu-header")
            with Vertical(classes="menu-body"):
                yield Button(" Quit ", id="exit-btn", classes="exit-menu-button")
                yield Button(" Clear Console ", id="clear-btn", classes="exit-menu-button")
                yield Button(" Cancel ", id="cancel-btn", classes="exit-menu-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-btn":
            self.app.exit()
        elif event.button.id == "clear-btn":
            console = self.app.query_one("#console-panel", Static)
            console.update("")
            self.app.pop_screen()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

class HelpMenu(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="help-menu-container"):
            yield Label(" 📖 HELP & SHORTCUTS ", id="menu-header")
            with Vertical(classes="menu-body"):
                yield Label("\nKey Bindings:", id="help-bindings-title")
                yield Label("ESC / q  - Open Exit Menu")
                yield Label("F1 / h / ? - Open Help Menu")
                yield Label("\nCommands:", id="help-commands-title")
                yield Label("c / Compile - Compiles selected file")
                yield Label("w / Watch   - Auto-compiles on change")
                yield Button(" Close ", id="close-help-btn", classes="help-menu-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-help-btn":
            self.app.pop_screen()

class Mark2TeXApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Mark2TeX Dashboard"
    BINDINGS = [
        ("escape", "show_exit_menu", "Exit Menu"),
        ("f1", "show_help_menu", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-layout"):
            with Vertical(id="file-explorer"):
                yield Label("📁 Markdown Files", id="explorer-title")
                yield ListView(id="file-list")
            with Vertical(id="config-panel"):
                # Welcome Panel
                with Vertical(id="welcome-panel"):
                    logo_text = render_logo_to_text("M2T/M2T_2.png", width=40)
                    yield Static(logo_text, id="welcome-logo", expand=True)
                    yield Label(
                        "📖 Guia Rápido:\n"
                        "1. Use as setas (← → ↑ ↓) ou (h j k l) para navegar\n"
                        "2. Selecione o arquivo .md\n"
                        "3. Selecione o template de saída\n"
                        "4. Pressione 'c' para Compilar ou 'w' para Watch\n\n"
                        "⌨️ Atalhos:\n"
                        "q / ESC - Menu de Saída\n"
                        "h / ? / F1 - Ajuda",
                        id="welcome-instructions"
                    )

                yield Label("⚙️ Build Configuration", id="config-title")
                yield Label("Select Template:")
                yield ListView(
                    ListItem(Label("tcc")),
                    ListItem(Label("artigo")),
                    ListItem(Label("projeto")),
                    id="template-list"
                )
                yield Button("🚀 Compile Now", id="compile-btn")
                yield Button("👀 Watch Mode: OFF", id="watch-btn")

        yield ProgressBar(id="progress-bar")
        yield Static("Console output will appear here...", id="console-panel")
        yield Footer()

    def on_key(self, event) -> None:
        key = event.key.lower() if hasattr(event.key, 'lower') else event.key

        # --- Global Quick Actions (btop style) ---
        if key == "q":
            self.action_show_exit_menu()
            return
        elif key in ("h", "?"):
            self.action_show_help_menu()
            return
        elif key == "c":
            self.compile_document()
            return
        elif key == "w":
            self.toggle_watch_mode()
            return

        # --- Navigation (Arrows & Vim-style) ---
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

    def action_show_exit_menu(self) -> None:
        self.push_screen(ExitMenu())

    def action_show_help_menu(self) -> None:
        self.push_screen(HelpMenu())

    def on_mount(self) -> None:
        self.docker_manager = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching = False
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
                self.query_one("#console-panel", Static).update("❌ Select file and template first to enable Watch Mode.")
                return

            self.watcher_manager.start_watching(
                selected_file,
                selected_template,
                self.compile_document
            )
            self.is_watching = True
            btn.label = "👀 Watch Mode: ON"
            self.query_one("#console-panel", Static).update(f"🔭 Watch Mode enabled for {selected_file}...")
        else:
            self.watcher_manager.stop_watching()
            self.is_watching = False
            btn.label = "👀 Watch Mode: OFF"
            self.query_one("#console-panel", Static).update("💤 Watch Mode disabled.")

    def compile_document(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        template_list = self.query_one("#template-list", ListView)
        console = self.query_one("#console-panel", Static)
        progress_bar = self.query_one("#progress-bar", ProgressBar)

        progress_bar.progress = 0

        selected_file = None
        if file_list.highlighted_child:
            selected_file = str(file_list.highlighted_child.query_one(Label).renderable)

        selected_template = None
        if template_list.highlighted_child:
            selected_template = str(template_list.highlighted_child.query_one(Label).renderable)

        if not selected_file or not selected_template:
            console.update("❌ Please select both a file and a template.")
            return

        console.update(f"🚀 Compiling {selected_file} with {selected_template}...\n")

        for line in self.docker_manager.compile(selected_file, selected_template):
            # Parse progress markers
            progress_match = re.search(r"PROGRESS:(\d+)%", line)
            if progress_match:
                percent = int(progress_match.group(1))
                progress_bar.progress = percent / 100
                continue # Do not print progress markers to console

            translated_line = LogTranslator.translate(line)
            console.update(console.renderable + "\n" + translated_line)

if __name__ == "__main__":
    app = Mark2TeXApp()
    app.run()
