"""Unit tests for mark2tex.info_panel.

Covers:
- CompilationInfo dataclass defaults and field mutation
- make_timestamp() format
- InfoPanelWidget.render() output for all status branches and edge cases
"""
from __future__ import annotations

import re
from unittest.mock import MagicMock

from mark2tex.info_panel import CompilationInfo, InfoPanelWidget, make_timestamp

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_text(widget: InfoPanelWidget) -> str:
    """Return the plain-text content of widget.render()."""
    result = widget.render()
    # Rich Text objects expose their plain representation via .plain
    return result.plain


# ---------------------------------------------------------------------------
# CompilationInfo
# ---------------------------------------------------------------------------

class TestCompilationInfo:
    def test_default_filename(self):
        assert CompilationInfo().filename == "—"

    def test_default_pages_is_none(self):
        assert CompilationInfo().pages is None

    def test_default_template(self):
        assert CompilationInfo().template == "—"

    def test_default_last_compiled_is_none(self):
        assert CompilationInfo().last_compiled is None

    def test_default_status_is_none(self):
        assert CompilationInfo().status is None

    def test_default_sections_is_empty_list(self):
        info = CompilationInfo()
        assert info.sections == []

    def test_default_warnings_is_empty_list(self):
        info = CompilationInfo()
        assert info.warnings == []

    def test_sections_are_not_shared_between_instances(self):
        a = CompilationInfo()
        b = CompilationInfo()
        a.sections.append("X")
        assert b.sections == []

    def test_warnings_are_not_shared_between_instances(self):
        a = CompilationInfo()
        b = CompilationInfo()
        a.warnings.append("W")
        assert b.warnings == []

    def test_fields_set_on_construction(self):
        info = CompilationInfo(
            filename="doc.md",
            pages=42,
            template="tcc-abnt",
            last_compiled="10:00:00",
            status="success",
            sections=["1. Intro"],
            warnings=["Overfull hbox"],
        )
        assert info.filename == "doc.md"
        assert info.pages == 42
        assert info.template == "tcc-abnt"
        assert info.last_compiled == "10:00:00"
        assert info.status == "success"
        assert info.sections == ["1. Intro"]
        assert info.warnings == ["Overfull hbox"]


# ---------------------------------------------------------------------------
# make_timestamp
# ---------------------------------------------------------------------------

class TestMakeTimestamp:
    _HH_MM_SS = re.compile(r"^\d{2}:\d{2}:\d{2}$")

    def test_format_matches_hhmmss(self):
        ts = make_timestamp()
        assert self._HH_MM_SS.match(ts), f"Unexpected format: {ts!r}"

    def test_returns_string(self):
        assert isinstance(make_timestamp(), str)

    def test_hours_in_range(self):
        h = int(make_timestamp().split(":")[0])
        assert 0 <= h <= 23

    def test_minutes_in_range(self):
        m = int(make_timestamp().split(":")[1])
        assert 0 <= m <= 59

    def test_seconds_in_range(self):
        s = int(make_timestamp().split(":")[2])
        assert 0 <= s <= 59


# ---------------------------------------------------------------------------
# InfoPanelWidget — render()
# ---------------------------------------------------------------------------

class TestInfoPanelWidgetRender:
    """Tests that exercise InfoPanelWidget.render() directly.

    Widget.__init__ requires a Textual app context for some internals;
    we bypass this by instantiating without calling the Textual event loop
    and invoking render() directly.
    """

    def _make_widget(self, info: CompilationInfo | None = None) -> InfoPanelWidget:
        widget = object.__new__(InfoPanelWidget)
        widget._info = info if info is not None else CompilationInfo()
        return widget

    # ── status branches ────────────────────────────────────────────────

    def test_success_status_shows_checkmark(self):
        w = self._make_widget(CompilationInfo(status="success"))
        assert "✅" in _render_text(w)

    def test_error_status_shows_cross(self):
        w = self._make_widget(CompilationInfo(status="error"))
        assert "❌" in _render_text(w)

    def test_none_status_shows_hourglass(self):
        w = self._make_widget(CompilationInfo(status=None))
        assert "⏳" in _render_text(w)

    # ── metadata presence ──────────────────────────────────────────────

    def test_filename_in_output(self):
        w = self._make_widget(CompilationInfo(filename="meu_tcc.md"))
        assert "meu_tcc.md" in _render_text(w)

    def test_pages_in_output(self):
        w = self._make_widget(CompilationInfo(pages=87))
        assert "87" in _render_text(w)

    def test_pages_none_shows_dash(self):
        w = self._make_widget(CompilationInfo(pages=None))
        assert "—" in _render_text(w)

    def test_template_in_output(self):
        w = self._make_widget(CompilationInfo(template="artigo-ieee"))
        assert "artigo-ieee" in _render_text(w)

    def test_timestamp_in_output(self):
        w = self._make_widget(CompilationInfo(last_compiled="14:32:01"))
        assert "14:32:01" in _render_text(w)

    def test_timestamp_none_shows_dash(self):
        w = self._make_widget(CompilationInfo(last_compiled=None))
        assert "—" in _render_text(w)

    # ── sections ──────────────────────────────────────────────────────

    def test_sections_appear_in_output(self):
        w = self._make_widget(CompilationInfo(sections=["1. Introduction", "  2. Methods"]))
        rendered = _render_text(w)
        assert "1. Introduction" in rendered
        assert "2. Methods" in rendered

    def test_empty_sections_shows_no_sections_fallback(self):
        w = self._make_widget(CompilationInfo(sections=[]))
        rendered = _render_text(w)
        # The i18n key info.no_sections must appear
        from mark2tex.i18n import t
        assert t("info.no_sections") in rendered

    # ── warnings ──────────────────────────────────────────────────────

    def test_warnings_appear_in_output(self):
        w = self._make_widget(CompilationInfo(warnings=["Overfull \\hbox"]))
        assert "Overfull" in _render_text(w)

    def test_empty_warnings_shows_no_warnings_fallback(self):
        w = self._make_widget(CompilationInfo(warnings=[]))
        from mark2tex.i18n import t
        assert t("info.no_warnings") in _render_text(w)

    # ── update_info ───────────────────────────────────────────────────

    def test_update_info_replaces_snapshot(self):
        w = self._make_widget(CompilationInfo(filename="old.md"))
        new_info = CompilationInfo(filename="new.md")
        # Patch refresh so it does not require app context
        w.refresh = MagicMock()
        w.update_info(new_info)
        assert w._info.filename == "new.md"
        w.refresh.assert_called_once()

    def test_update_info_does_not_mutate_original(self):
        original = CompilationInfo(filename="original.md")
        w = self._make_widget(original)
        w.refresh = MagicMock()
        w.update_info(CompilationInfo(filename="other.md"))
        assert original.filename == "original.md"
