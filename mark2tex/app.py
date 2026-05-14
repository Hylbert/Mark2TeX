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
    TabbedContent,
    TabPane,
)

from . import config as cfg
from .docker_manager import DockerManager
from .frontmatter_validator import validate as validate_frontmatter
from .i18n import set_language, t
from .info_panel import CompilationInfo, InfoPanelWidget, make_timestamp
from .log_translator import LogTranslator
from .onboarding import OnboardingScreen, is_first_run
from .settings_screen import LanguageChanged, SettingsScreen
from .utils.doc_structure import extract_sections
from .utils.visuals import M2TBannerWidget, M2TMenuOption
from .watcher import WatcherManager
from .yaml_inject_screen import YamlInjectScreen
from .yaml_injector import has_frontmatter, inject_frontmatter, swap_template

# ---------------------------------------------------------------------------
# Fontes disponíveis: (id interno, rótulo exibido na TUI)
# ---------------------------------------------------------------------------
AVAILABLE_FONTS: list[tuple[str, str]] = [
    ("times",     "Liberation Serif  (Times)"),
    ("arial",     "Liberation Sans   (Arial)"),
    ("helvetica", "Nimbus Sans       (Helvetica)"),
    ("ubuntu",    "Ubuntu"),
]

# Maximum number of characters rendered in the preview panel.
# Large documents (e.g. 60+ page TCCs) can freeze the Textual event loop
# when the full content is passed to the Markdown widget at once.
_PREVIEW_MAX_CHARS = 8_000
_PREVIEW_TRUNCATED_SUFFIX = "\n\n---\n_Preview truncated. Open the file in your editor to see the full content._"

# ---------------------------------------------------------------------------
# Progress milestones emitted by build.sh via PROGRESS:N% tokens.
# Each value is the CEILING (exclusive) that bump is allowed to reach before
# the next official token arrives.  build.sh emits the milestone itself, so
# the ceiling is always (next_milestone - 1).
#
# Ordered ascending — _progress_ceiling() does a linear scan.
# ---------------------------------------------------------------------------
_PROGRESS_MILESTONES: tuple[int, ...] = (10, 40, 50, 60, 75, 88, 94, 100)


def _bump_ceiling(current: int) -> int:
    """Return the highest value bump may reach given the current progress.

    The ceiling is (next_milestone - 1) so the bar never jumps past the
    value that build.sh will emit next, preventing rewinds.
    """
    for milestone in _PROGRESS_MILESTONES:
        if current < milestone:
            return milestone - 1
    return 99  # already at or past last milestone — cap at 99


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
    """Copia texto para a área de transferência."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return
    except Exception:  # noqa: BLE001
        pass

    for cmd in (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=text.encode(), check=True, timeout=3)
                return
            except Exception:  # noqa: BLE001
                continue

    raise RuntimeError(
        "Nenhum mecanismo de clipboard disponível.\n"
        "Instale: xclip, xsel ou wl-clipboard (Wayland)."
    )


def _pdf_exists_for(md_path: str) -> bool:
    """Return True if a PDF was produced next to the source Markdown file."""
    pdf = Path(md_path).with_suffix(".pdf")
    return pdf.exists() and pdf.stat().st_size > 0


class OptionItem(ListItem):
    def __init__(self, label_text: str, item_id: str | None = None) -> None:
        super().__init__(Label(label_text), id=item_id)
        self.label_text = label_text


class DirItem(ListItem):
    """Item de diretório na lista de arquivos. Guarda o Path absoluto do destino."""

    def __init__(self, display_label: str, target: Path) -> None:
        super().__init__(Label(display_label))
        self.display_label = display_label
        self.target = target
        self.add_class("dir-item")


class FontItem(ListItem):
    """Item de fonte na lista da TUI. Guarda o id interno da fonte."""

    def __init__(self, font_id: str, display_label: str) -> None:
        super().__init__(Label(display_label))
        self.font_id = font_id
        self.display_label = display_label


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
                yield Label("Tab          — " + ("Navigate panels" if t("menu.exit") == "EXIT" else "Navegar entre painéis"))
                yield Label("↑ ↓          — " + ("Navigate lists" if t("menu.exit") == "EXIT" else "Navegar nas listas"))
                yield Label("Enter        — " + ("Enter folder / select file / confirm template" if t("menu.exit") == "EXIT" else "Entrar na pasta / selecionar arquivo / confirmar template"))
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
                            yield Label(t("status.font"),     id="status-font")
                        with Horizontal(id="selector-row"):
                            with Vertical(id="template-col"):
                                yield Label(t("panel.template_label"), id="template-title")
                                yield ListView(id="template-list")
                            with Vertical(id="font-col"):
                                yield Label(t("panel.font_label"), id="font-title")
                                yield ListView(id="font-list")
                        with Horizontal(id="action-bar"):
                            yield Button(t("btn.compile"),   id="compile-btn")
                            yield Button(t("btn.watch_off"), id="watch-btn")
                yield ProgressBar(id="progress-bar", total=100)
                with Horizontal(id="console-bar"):
                    yield Button("⊙", id="copy-console-btn", classes="console-action-btn")
                yield RichLog(id="console-panel", highlight=False, markup=False, wrap=True)
            with Vertical(id="preview-panel"):
                with TabbedContent(id="preview-tabs", initial="tab-md"):
                    with TabPane(t("info.tab_markdown"), id="tab-md"):
                        with ScrollableContainer(id="preview-scroll"):
                            yield Markdown("", id="preview-content")
                    with TabPane(t("info.tab_pdf"), id="tab-pdf", disabled=True):
                        yield InfoPanelWidget(id="info-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.docker_manager  = DockerManager()
        self.watcher_manager = WatcherManager()
        self.is_watching      = False
        self.selected_file:     str | None = None
        self.selected_template: str | None = None
        self.selected_font:     str | None = None
        self._console_lines:    list[str]  = []
        self._current_dir:      Path       = Path.cwd()
        self._refresh_ui_labels()
        self._populate_templates()
        self._populate_fonts()
        self._populate_files()
        if is_first_run():
            self.call_after_refresh(
                self.push_screen,
                OnboardingScreen(),
                self._on_onboarding_dismissed,
            )

    def _on_onboarding_dismissed(self, refresh_files: bool) -> None:
        """Called automatically by Textual when OnboardingScreen.dismiss() fires."""
        if refresh_files:
            self._populate_files()

    def _populate_templates(self) -> None:
        template_list = self.query_one("#template-list", ListView)
        template_list.clear()
        for name in self.docker_manager.list_templates():
            template_list.append(OptionItem(name))

    def _populate_fonts(self) -> None:
        font_list = self.query_one("#font-list", ListView)
        font_list.clear()
        for font_id, label in AVAILABLE_FONTS:
            font_list.append(FontItem(font_id, label))

    def _populate_files(self) -> None:
        """Populate the file list with dirs-first then .md files for _current_dir."""
        file_list = self.query_one("#file-list", ListView)
        file_list.clear()

        folder_name = self._current_dir.name or str(self._current_dir)
        self.query_one("#file-explorer").border_title = folder_name

        cwd_root = Path.cwd()
        if self._current_dir != cwd_root:
            parent = self._current_dir.parent
            file_list.append(DirItem("📁 ../", target=parent))

        try:
            entries = list(self._current_dir.iterdir())
        except PermissionError:
            return

        subdirs = sorted(
            [e for e in entries if e.is_dir() and not e.name.startswith(".")],
            key=lambda p: p.name.lower(),
        )
        md_files = sorted(
            [
                e for e in entries
                if e.is_file()
                and e.suffix == ".md"
                # Exclude the ephemeral pre-processed copy written by build.sh
                # (e.g. thesis._processed.md) so it never appears in the
                # file browser as a selectable document.
                and not e.name.endswith("._processed.md")
            ],
            key=lambda p: p.name.lower(),
        )

        for d in subdirs:
            file_list.append(DirItem(f"📁 {d.name}/", target=d))

        for f in md_files:
            item = OptionItem(f.name)
            if not has_frontmatter(str(f)):
                item.add_class("file-item--no-yaml")
            file_list.append(item)

    def _navigate_to(self, target: Path) -> None:
        """Change the current directory and refresh the file list."""
        self.selected_file = None
        self.query_one("#status-file", Label).update(t("status.file"))
        self._current_dir = target.resolve()
        self._populate_files()

    def _refresh_ui_labels(self) -> None:
        self.query_one("#file-explorer").border_title  = t("panel.files")
        self.query_one("#config-panel").border_title   = t("panel.config")
        self.query_one("#preview-panel").border_title  = t("panel.preview")
        self.query_one("#console-panel").border_title  = t("panel.console")
        self.query_one("#template-title", Label).update(t("panel.template_label"))
        self.query_one("#font-title",     Label).update(t("panel.font_label"))
        self.query_one("#status-file",     Label).update(t("status.file"))
        self.query_one("#status-template", Label).update(t("status.template"))
        self.query_one("#status-font",     Label).update(t("status.font"))
        self.query_one("#compile-btn",     Button).label = t("btn.compile")
        if not self.is_watching:
            self.query_one("#watch-btn", Button).label = t("btn.watch_off")

    def on_language_changed(self, _: LanguageChanged) -> None:
        self._refresh_ui_labels()

    def _apply_template_swap(self, new_template: str) -> None:
        """If a file with frontmatter is selected, patch its header surgically."""
        if not self.selected_file:
            return
        abs_file = str(self._current_dir / self.selected_file)
        if not has_frontmatter(abs_file):
            return
        ok = swap_template(abs_file, new_template)
        if ok:
            self._log_console(
                t("yaml.template_swapped").format(template=new_template),
                style="#4caf87",
            )
            self._update_preview(self.selected_file)
        else:
            self._log_console(
                t("yaml.template_swap_err").format(msg="I/O error"),
                style="#e05c5c",
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if event.list_view.id == "file-list":
            if isinstance(item, DirItem):
                self._navigate_to(item.target)
                return
            if isinstance(item, OptionItem):
                self.selected_file = item.label_text
                self.query_one("#status-file", Label).update(f"Arquivo  : {self.selected_file}")
        elif event.list_view.id == "template-list" and isinstance(item, OptionItem):
            self.selected_template = item.label_text
            self.query_one("#status-template", Label).update(f"Template : {self.selected_template}")
            self._apply_template_swap(item.label_text)
        elif event.list_view.id == "font-list" and isinstance(item, FontItem):
            self.selected_font = item.font_id
            self.query_one("#status-font", Label).update(f"Fonte    : {item.display_label}")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if event.list_view.id == "file-list":
            if isinstance(item, DirItem):
                return
            if isinstance(item, OptionItem):
                self.selected_file = item.label_text
                self.query_one("#status-file", Label).update(f"Arquivo  : {self.selected_file}")
                self._update_preview(item.label_text)
                self._check_yaml_badge(item)
                self._reset_info_tab()
        elif event.list_view.id == "template-list" and isinstance(item, OptionItem):
            # Only update the status label as visual feedback while browsing.
            # The actual swap is confirmed on Enter (on_list_view_selected).
            self.query_one("#status-template", Label).update(f"Template : {item.label_text}")
        elif event.list_view.id == "font-list" and isinstance(item, FontItem):
            self.selected_font = item.font_id
            self.query_one("#status-font", Label).update(f"Fonte    : {item.display_label}")

    def _check_yaml_badge(self, item: OptionItem) -> None:
        """Add/remove the no-yaml CSS class based on frontmatter presence."""
        filepath = str(self._current_dir / item.label_text)
        if not has_frontmatter(filepath):
            item.add_class("file-item--no-yaml")
        else:
            item.remove_class("file-item--no-yaml")

    def _reset_info_tab(self) -> None:
        tab = self.query_one("#tab-pdf", TabPane)
        tab.disabled = True
        self.query_one("#preview-tabs", TabbedContent).active = "tab-md"

    def _update_preview(self, filename: str) -> None:
        filepath = self._current_dir / filename
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, PermissionError, OSError):
            content = f"_Could not read file `{filename}`._"
        if len(content) > _PREVIEW_MAX_CHARS:
            content = content[:_PREVIEW_MAX_CHARS] + _PREVIEW_TRUNCATED_SUFFIX
        preview = self.query_one("#preview-content", Markdown)
        self.call_after_refresh(preview.update, content)

    def _get_selection(self) -> tuple[str | None, str | None, str | None]:
        return self.selected_file, self.selected_template, self.selected_font

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
        btn.label = "⊙"
        btn.remove_class("console-action-btn--copied")

    def _log_console(self, message: str, style: str = "white") -> None:
        self._console_lines.append(message)
        console = self.query_one("#console-panel", RichLog)
        console.write(Text(message, style=style))
        console.scroll_end()

    def _set_progress(self, value: int) -> None:
        self.query_one("#progress-bar", ProgressBar).update(progress=value)

    def _run_frontmatter_warnings(self, abs_file: str, selected_template: str) -> None:
        """Log frontmatter validation warnings in yellow. Never blocks compilation."""
        errors = validate_frontmatter(abs_file, selected_template)
        if not errors:
            return
        self._log_console(t("validator.warnings_header"), style="#e0a24a")
        for err in errors:
            self._log_console(err.message, style="#e0a24a")

    def toggle_watch_mode(self) -> None:
        btn = self.query_one("#watch-btn", Button)
        if not self.is_watching:
            selected_file, selected_template, selected_font = self._get_selection()
            if not selected_file or not selected_template:
                self._log_console(t("compile.select_watch"), style="#e05c5c")
                return
            abs_file = str(self._current_dir / selected_file)
            self.watcher_manager.start_watching(
                abs_file,
                selected_template,
                lambda: self.compile_specific_document(
                    selected_file,
                    self.selected_template or selected_template,
                    selected_font,
                ),
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
        selected_file, selected_template, selected_font = self._get_selection()
        if not selected_file or not selected_template:
            self._log_console(t("compile.select_file"), style="#e05c5c")
            return
        abs_file = str(self._current_dir / selected_file)
        if not has_frontmatter(abs_file):
            self.push_screen(
                YamlInjectScreen(abs_file, selected_template),
                lambda confirmed: self._on_yaml_inject_dismissed(
                    confirmed, selected_file, selected_template, selected_font
                ),
            )
            return
        self._run_frontmatter_warnings(abs_file, selected_template)
        self.compile_specific_document(selected_file, selected_template, selected_font)

    def _on_yaml_inject_dismissed(
        self,
        confirmed: bool,
        selected_file: str,
        selected_template: str,
        selected_font: str | None,
    ) -> None:
        """Called when YamlInjectScreen closes."""
        if not confirmed:
            return
        abs_file = str(self._current_dir / selected_file)
        ok = inject_frontmatter(abs_file, selected_template)
        if ok:
            self._log_console(t("yaml.injected_ok"), style="#4caf87")
            self._populate_files()
            self.compile_specific_document(selected_file, selected_template, selected_font)
        else:
            self._log_console(
                t("yaml.injected_err").format(msg="permission denied or I/O error"),
                style="#e05c5c",
            )

    def compile_specific_document(
        self,
        selected_file: str,
        selected_template: str,
        selected_font: str | None = None,
    ) -> None:
        # Kill any running Docker container before starting a new one.
        # This ensures the old container's cleanup() trap finishes before
        # Pandoc regenerates the .tex file in the new run.
        self.docker_manager.abort()
        self.run_worker(
            lambda: self._run_compilation(
                str(self._current_dir / selected_file),
                selected_template,
                selected_font,
            ),
            thread=True,
            exclusive=True,
            group="compile",
            description=f"Compile {selected_file}",
        )

    def _run_compilation(
        self,
        selected_file: str,
        selected_template: str,
        selected_font: str | None,
    ) -> None:
        def ui(action: str, value=None) -> None:
            _logger.debug("UI REQUEST - %s: %s", action, value)
            self.call_from_thread(self._apply_ui_update, action, value)

        # One translator instance per compilation run so that stateful
        # multi-line sequences (error + l.N location, polyglossia
        # continuation blocks) are handled correctly across line boundaries.
        translator = LogTranslator()

        ui("progress", 0)
        ui("console", (f"{t('compile.start')} {selected_file} com template '{selected_template}'...", "#5ab4bc"))
        if selected_font:
            ui("console", (f"🔤 {t('font.using')} {selected_font}", "#5ab4bc"))

        status = "error"
        pages: int | None = None
        warnings: list[str] = []

        try:
            for line in self.docker_manager.compile(
                selected_file, selected_template, font=selected_font
            ):
                clean = line.strip()
                if not clean:
                    continue
                _logger.debug("RAW LINE: %s", line)
                result = translator.translate(clean)
                if result is None:
                    continue
                if result.startswith("__PROGRESS__"):
                    percent = int(result.removeprefix("__PROGRESS__"))
                    # Official milestone: jump directly, no ceiling check needed.
                    ui("progress", percent)
                    ui("console", (f"⏳ Processing... {percent}%", "white"))
                    if percent == 100:
                        status = "success"
                    continue
                # Bump the bar by 1 for ⚠️/❌/🔄 lines, but never cross
                # into the next milestone's territory (avoids rewinds).
                if result.startswith(("⚠️", "⚠", "❌", "🔄")):
                    ui("progress_bump", None)
                if result.startswith(("⚠️", "⚠")):
                    warnings.append(result)
                # Parse page count from latexmk output line
                if "páginas" in result or "pages" in result.lower():
                    import re
                    m = re.search(r"(\d+)\s+p[áa]g", result)
                    if not m:
                        m = re.search(r"(\d+)\s+page", result, re.IGNORECASE)
                    if m:
                        pages = int(m.group(1))
                ui("console", (result, "white"))
        except Exception as exc:  # noqa: BLE001
            ui("console", (f"{t('compile.error')}: {exc}", "#e05c5c"))

        # If the process exited with a non-zero code but the PDF was still
        # written to disk (common with xelatex non-fatal warnings), treat
        # the compilation as successful so the info panel reflects reality.
        if status == "error" and _pdf_exists_for(selected_file):
            status = "success"

        ui("compilation_done", (status, pages, warnings, selected_file))

    def _apply_ui_update(self, action: str, value=None) -> None:
        _logger.debug("UI APPLY - %s: %s", action, value)
        try:
            if action == "progress":
                self._set_progress(int(value))
            elif action == "progress_bump":
                bar = self.query_one("#progress-bar", ProgressBar)
                current = int(bar.progress or 0)
                ceiling = _bump_ceiling(current)
                if current < ceiling:
                    self._set_progress(current + 1)
            elif action == "console":
                message, style = value
                self._log_console(message, style=style)
            elif action == "compilation_done":
                status, pages, warnings, md_path = value
                info = CompilationInfo(
                    filename=self.selected_file or "—",
                    pages=pages,
                    template=self.selected_template or "—",
                    last_compiled=make_timestamp(),
                    status=status,
                    sections=extract_sections(md_path) if md_path else [],
                    warnings=warnings,
                )
                self.query_one("#info-panel", InfoPanelWidget).update_info(info)
                tab = self.query_one("#tab-pdf", TabPane)
                tab.disabled = False
                self.query_one("#preview-tabs", TabbedContent).active = "tab-pdf"
        except Exception as exc:  # noqa: BLE001
            print(f"[UI Error] {action}: {exc}")


if __name__ == "__main__":
    Mark2TeXApp().run()
