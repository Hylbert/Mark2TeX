import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Button, Static
from textual.containers import Horizontal, Vertical

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
        # Populate file list with .md files in current directory
        files = [f for f in os.listdir('.') if f.endswith('.md')]
        file_list = self.query_one("#file-list", ListView)
        for f in files:
            file_list.append(ListItem(Label(f)))

if __name__ == "__main__":
    app = Mark2TeXApp()
    app.run()
