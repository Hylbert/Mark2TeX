"""Onboarding: first-run detection, welcome screen and ``mark2tex init``."""
from __future__ import annotations

import shutil
from pathlib import Path

from platformdirs import user_data_dir
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, LoadingIndicator

from .i18n import t

# ---------------------------------------------------------------------------
# Flag file helpers
# ---------------------------------------------------------------------------

_APP_NAME = "mark2tex"


def _flag_path() -> Path:
    """Return the path of the first-run sentinel file (cross-platform)."""
    return Path(user_data_dir(_APP_NAME, appauthor=False)) / ".onboarding_done"


def is_first_run() -> bool:
    """Return True when the onboarding has never been completed."""
    return not _flag_path().exists()


def mark_onboarding_done() -> None:
    """Write the sentinel file so the screen is not shown again."""
    flag = _flag_path()
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()


def reset_onboarding() -> None:  # pragma: no cover — developer helper
    """Remove the sentinel so the onboarding runs again on next launch."""
    flag = _flag_path()
    if flag.exists():
        flag.unlink()


# ---------------------------------------------------------------------------
# ``mark2tex init`` — copy template + example to cwd
# ---------------------------------------------------------------------------


def run_init(template: str | None = None) -> None:
    """Copy a starter template and example file into the current directory."""
    from importlib import resources

    from rich.console import Console

    console = Console()

    try:
        templates_path = Path(str(resources.files("mark2tex").joinpath("templates")))
    except Exception as exc:  # noqa: BLE001
        console.print(f"[#e05c5c]✗ Could not locate templates: {exc}[/]")
        return

    available = sorted(
        d.name for d in templates_path.iterdir() if d.is_dir()
    )

    if not available:
        console.print("[#e05c5c]✗ No templates found in the package.[/]")
        return

    # Choose template
    if template is None:
        console.print(
            "[#03656b]Available templates:[/] "
            + ", ".join(f"[bold]{n}[/bold]" for n in available)
        )
        console.print("[#888888]Tip: run `mark2tex init --template NAME` to skip this prompt.[/]")
        try:
            template = input("Template name: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[#e0a24a]⚠️  Aborted.[/]")
            return

    if template not in available:
        console.print(
            f"[#e05c5c]✗ Template '[bold]{template}[/bold]' not found.[/]\n"
            f"  Available: {', '.join(available)}"
        )
        return

    src_dir = templates_path / template
    dest_dir = Path.cwd()

    copied: list[str] = []
    skipped: list[str] = []

    for src_file in src_dir.rglob("*"):
        if not src_file.is_file():
            continue
        rel = src_file.relative_to(src_dir)
        dest_file = dest_dir / rel
        if dest_file.exists():
            skipped.append(str(rel))
            continue
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        copied.append(str(rel))

    for name in copied:
        console.print(f"[#4caf87]✔ Copied:[/]  {name}")
    for name in skipped:
        console.print(f"[#e0a24a]⚠  Skipped (already exists):[/] {name}")

    if copied:
        console.print(
            f"\n[#03656b bold]✔ Template '[bold white]{template}[/bold white]' ready.[/] "
            "Edit the example file and run [bold]mark2tex[/bold] to compile."
        )
    else:
        console.print("[#888888]Nothing new to copy — all files already exist.[/]")

    mark_onboarding_done()


def _run_init_headless(template: str | None = None) -> tuple[bool, str]:
    """Run init without Rich Console output; return (success, message).

    Used when init is triggered from within the TUI so we can capture the
    result and display it inside the Textual screen instead of writing to
    stdout.
    """
    from importlib import resources

    try:
        templates_path = Path(str(resources.files("mark2tex").joinpath("templates")))
    except Exception as exc:  # noqa: BLE001
        return False, f"Could not locate templates: {exc}"

    available = sorted(d.name for d in templates_path.iterdir() if d.is_dir())

    if not available:
        return False, "No templates found in the package."

    if template is None:
        # Pick the first available template automatically when called from TUI.
        template = available[0]

    if template not in available:
        return False, f"Template '{template}' not found. Available: {', '.join(available)}"

    src_dir = templates_path / template
    dest_dir = Path.cwd()

    copied: list[str] = []
    skipped: list[str] = []

    for src_file in src_dir.rglob("*"):
        if not src_file.is_file():
            continue
        rel = src_file.relative_to(src_dir)
        dest_file = dest_dir / rel
        if dest_file.exists():
            skipped.append(str(rel))
            continue
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        copied.append(str(rel))

    if copied:
        msg = t("onboarding.init_done").format(template=template, n=len(copied))
    else:
        msg = t("onboarding.init_nothing")

    mark_onboarding_done()
    return True, msg


# ---------------------------------------------------------------------------
# Onboarding Textual Screen
# ---------------------------------------------------------------------------


class OnboardingScreen(ModalScreen):
    """Welcome screen shown automatically on the first run."""

    BINDINGS = [
        Binding("escape", "dismiss_screen", show=False),
        Binding("enter",  "dismiss_screen", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="ob-window"):
            yield Label(t("onboarding.title"),    id="ob-title")
            yield Label(t("onboarding.welcome"),  id="ob-welcome")
            yield Label("",                        id="ob-spacer1")
            yield Label(t("onboarding.what"),     id="ob-what")
            yield Label("",                        id="ob-spacer2")
            yield Label(t("onboarding.steps"),    id="ob-steps")
            yield Label("",                        id="ob-spacer3")
            yield Label(t("onboarding.hint_init"), id="ob-hint")
            yield Label("",                        id="ob-spacer4")
            yield Button(t("onboarding.btn_start"),    id="ob-btn-start",    variant="default")
            yield Button(t("onboarding.btn_init"),     id="ob-btn-init",     variant="success")
            yield LoadingIndicator(id="ob-loading")
            yield Label("", id="ob-init-status")
            yield Label(t("onboarding.footer"),   id="ob-footer")

    def on_mount(self) -> None:
        # Hide loading indicator and status label until init is triggered.
        self.query_one("#ob-loading", LoadingIndicator).display = False
        self.query_one("#ob-init-status", Label).display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ob-btn-start":
            self._finish()
        elif event.button.id == "ob-btn-init":
            self._trigger_init()

    def action_dismiss_screen(self) -> None:
        self._finish()

    def _finish(self) -> None:
        mark_onboarding_done()
        self.dismiss()

    def _trigger_init(self) -> None:
        """Disable buttons, show spinner, run init in a worker."""
        self.query_one("#ob-btn-start", Button).disabled = True
        self.query_one("#ob-btn-init",  Button).disabled = True
        self.query_one("#ob-loading",   LoadingIndicator).display = True
        self.query_one("#ob-init-status", Label).display = False
        self.app.run_worker(self._run_init_worker, exclusive=True, thread=True)

    def _run_init_worker(self) -> None:
        """Worker: calls _run_init_headless and updates the UI via call_from_thread."""
        success, msg = _run_init_headless()
        self.app.call_from_thread(self._on_init_done, success, msg)

    def _on_init_done(self, success: bool, msg: str) -> None:
        """Called on the main thread once the worker finishes."""
        self.query_one("#ob-loading", LoadingIndicator).display = False
        status = self.query_one("#ob-init-status", Label)
        status.update(msg)
        status.set_class(not success, "ob-error")
        status.display = True

        if success:
            # Auto-dismiss after a short delay so the user can read the message.
            self.set_timer(1.8, self._finish)
        else:
            # Re-enable buttons so the user can retry or just close.
            self.query_one("#ob-btn-start", Button).disabled = False
            self.query_one("#ob-btn-init",  Button).disabled = False
