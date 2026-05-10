"""info_panel.py — InfoPanelWidget for the tabbed preview panel.

Renders a structured summary of the last PDF compilation result
directly inside the TUI, without requiring any external PDF viewer.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field

from rich.text import Text
from textual.app import RenderResult
from textual.widget import Widget

from .i18n import t


@dataclass
class CompilationInfo:
    """Snapshot of a single compilation run."""

    filename: str = "—"
    pages: int | None = None
    template: str = "—"
    last_compiled: str | None = None   # HH:MM:SS string
    status: str | None = None          # "success" | "error" | None
    sections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class InfoPanelWidget(Widget):
    """Textual widget that displays a CompilationInfo summary.

    Call :meth:`update_info` after each compilation run to refresh the
    panel content.  The widget is intentionally read-only — it never
    mutates the passed dataclass.
    """

    DEFAULT_CSS = """
    InfoPanelWidget {
        height: 1fr;
        padding: 1 2;
        background: transparent;
        color: #fafafa;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._info = CompilationInfo()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_info(self, info: CompilationInfo) -> None:
        """Replace the current snapshot and trigger a re-render."""
        self._info = info
        self.refresh()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> RenderResult:  # type: ignore[override]
        i = self._info
        text = Text(no_wrap=False)

        # ── Header: filename ──────────────────────────────────────────
        text.append("📄  ", style="bold")
        text.append(i.filename, style="bold #fafafa")
        text.append("\n\n")

        # ── Metadata grid ────────────────────────────────────────────
        pages_val = str(i.pages) if i.pages is not None else "—"
        time_val = i.last_compiled or "—"

        if i.status == "success":
            status_val = "✅ " + t("info.status_success")
            status_style = "#4caf87"
        elif i.status == "error":
            status_val = "❌ " + t("info.status_error")
            status_style = "#e05c5c"
        else:
            status_val = "⏳ " + t("info.status_pending")
            status_style = "#e0a24a"

        def _row(label: str, value: str, value_style: str = "#b0b5ba") -> None:
            text.append(f"  {label:<22}", style="#7a7f84")
            text.append(f"{value}\n", style=value_style)

        _row(t("info.pages"), pages_val)
        _row(t("info.template"), i.template)
        _row(t("info.last_compiled"), time_val)
        _row(t("info.status"), status_val, value_style=status_style)

        # ── Document structure ────────────────────────────────────────
        text.append("\n")
        text.append(f" ── {t('info.structure')} ", style="bold #03656b")
        text.append("─" * 20 + "\n", style="#03656b")

        if i.sections:
            for entry in i.sections:
                text.append(f"  {entry}\n", style="#c8cdd2")
        else:
            text.append(f"  {t('info.no_sections')}\n", style="#555a5f italic")

        # ── Warnings ─────────────────────────────────────────────────
        text.append("\n")
        text.append(f" ── {t('info.warnings')} ", style="bold #e0a24a")
        text.append("─" * 20 + "\n", style="#e0a24a")

        if i.warnings:
            for w in i.warnings:
                text.append(f"  {w}\n", style="#e0c070")
        else:
            text.append(f"  {t('info.no_warnings')}\n", style="#555a5f italic")

        return text


def make_timestamp() -> str:
    """Return the current local time as HH:MM:SS."""
    return datetime.datetime.now().strftime("%H:%M:%S")
