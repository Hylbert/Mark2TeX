import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Button, Static
from textual.containers import Horizontal, Vertical
from .docker_manager import DockerManager
from .log_translator import LogTranslator

class Mark2TeXApp(App):
    CSS_PATH = "src/styles.tcss"
    TITLE = "Mark2TeX Dashboard"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="file-explorer"):
                yield Label("📁 Markdown Files", id="explorer-title")
                yield ListView(id="file-list")
            with Vertical(id="config-panel"):
                yield Label("⚙️ Build Configuration")
                yield Label("Select Template:")
                # Simplified template selection for base layout
                yield ListView(
                    ListItem(Label("tcc")),
                    ListItem(Label("artigo")),
                    ListItem(Label("projeto")),
                    id="template-list"
                )
                yield Button("🚀 Compile Now", id="compile-btn")
        yield Static("Console output will appear here...", id="console-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.docker_manager = DockerManager()
        # Populate file list with .md files in current directory
        files = [f for f in os.listdir('.') if f.endswith('.md')]
        file_list = self.query_one("#file-list", ListView)
        for f in files:
            file_list.append(ListItem(Label(f)))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compile-btn":
            self.compile_document()

    def compile_document(self) -> None:
        file_list = self.query_one("#file-list", ListView)
        template_list = self.query_one("#template-list", ListView)
        console = self.query_one("#console-panel", Static)

        selected_file = None
        if file_list.highlighted_child:
            selected_file = file_list.highlighted_child.query_one(Label).renderable

        selected_template = None
        if template_list.highlighted_child:
            selected_template = template_list.highlighted_child.query_one(Label).renderable

        if not selected_file or not selected_template:
            console.update("❌ Please select both a file and a template.")
            return

        console.update(f"🚀 Compiling {selected_file} with {selected_template}...\n")

        # In a real Textual app, this should be run in a worker to avoid blocking the UI
        # For the base implementation, we stream the lines
        for line in self.docker_manager.compile(selected_file, selected_template):
            translated_line = LogTranslator.translate(line)
            console.update(console.renderable + "\n" + translated_line)
    app = Mark2TeXApp()
    app.run()
