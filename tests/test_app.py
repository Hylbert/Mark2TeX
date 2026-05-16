"""Unit tests for Mark2TeXApp and module-level helpers.

All tests use direct method calls with a plain MagicMock standing in for a
fully-mounted Mark2TeXApp, or exercise pure module-level functions directly.
No Textual async event-loop is required.

Coverage targets
----------------
- ``_bump_ceiling``              — pure function, all milestone branches
- ``_pdf_exists_for``            — file exists / missing / empty
- ``_apply_template_swap``       — no file, no frontmatter, swap ok, swap fail
- ``toggle_watch_mode``          — start branch (template closure) + stop branch
- ``on_list_view_selected``      — file-list, template-list, font-list
- ``on_list_view_highlighted``   — template-list (label-only), file-list, font-list
- ``_get_selection``             — smoke
- ``_log_console``               — appends line, calls widget
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_app() -> MagicMock:
    """Return a plain MagicMock pre-loaded with every instance attribute that
    Mark2TeXApp.on_mount() sets dynamically.  We avoid ``spec=Mark2TeXApp``
    because those dynamic attributes are absent from the class object and
    would raise ``AttributeError`` under spec enforcement."""
    app = MagicMock()
    app.selected_template = None
    app.selected_file = None
    app.selected_font = None
    app.is_watching = False
    app.watcher_manager = MagicMock()
    app._current_dir = MagicMock()
    app._console_lines = []
    return app


def _make_event(list_view_id: str, item: object) -> SimpleNamespace:
    """Build a minimal fake ListView.Selected / ListView.Highlighted event."""
    lv = SimpleNamespace(id=list_view_id)
    return SimpleNamespace(list_view=lv, item=item)


def _option(label_text: str) -> SimpleNamespace:
    """Fake OptionItem with a label_text attribute."""
    return SimpleNamespace(label_text=label_text, id=None)


def _font_item(font_id: str, display_label: str) -> SimpleNamespace:
    """Fake FontItem."""
    return SimpleNamespace(font_id=font_id, display_label=display_label)


def _dir_item(target: Path) -> SimpleNamespace:
    """Fake DirItem."""
    return SimpleNamespace(target=target)


def _isinstance_patch(option_cls_name: str = "OptionItem"):
    """Return a context manager that makes isinstance() return True for the
    named class when the object is a SimpleNamespace (our fake item)."""
    import builtins

    real = builtins.isinstance

    def _fake(obj: object, cls: object) -> bool:  # noqa: ANN401
        import mark2tex.app as _app
        target = getattr(_app, option_cls_name, None)
        if target is not None and cls is target:
            return True
        if isinstance(cls, tuple):
            return any(_fake(obj, c) for c in cls)
        return real(obj, cls)  # type: ignore[arg-type]

    return patch("mark2tex.app.isinstance", side_effect=_fake)


# ---------------------------------------------------------------------------
# _bump_ceiling
# ---------------------------------------------------------------------------


class TestBumpCeiling:
    """_bump_ceiling returns (next_milestone - 1) for the current progress value
    and 99 once all milestones are passed."""

    def _ceil(self, value: int) -> int:
        from mark2tex.app import _bump_ceiling
        return _bump_ceiling(value)

    def test_zero_returns_below_first_milestone(self) -> None:
        # First milestone is 10 → ceiling is 9
        assert self._ceil(0) == 9

    def test_at_first_milestone_advances(self) -> None:
        # current=10 is no longer < 10, so next milestone is 40 → ceiling 39
        assert self._ceil(10) == 39

    def test_mid_range(self) -> None:
        assert self._ceil(41) == 49  # next milestone after 41 is 50

    def test_at_last_milestone_returns_99(self) -> None:
        assert self._ceil(100) == 99

    def test_beyond_last_milestone_returns_99(self) -> None:
        assert self._ceil(150) == 99

    def test_just_before_milestone_stays_below(self) -> None:
        # current=59 < 60 (milestone) → ceiling is 59 itself
        assert self._ceil(59) == 59


# ---------------------------------------------------------------------------
# _pdf_exists_for
# ---------------------------------------------------------------------------


class TestPdfExistsFor:
    def test_returns_true_when_pdf_present(self, tmp_path: Path) -> None:
        from mark2tex.app import _pdf_exists_for

        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"%PDF content")
        assert _pdf_exists_for(str(tmp_path / "doc.md")) is True

    def test_returns_false_when_pdf_missing(self, tmp_path: Path) -> None:
        from mark2tex.app import _pdf_exists_for

        assert _pdf_exists_for(str(tmp_path / "doc.md")) is False

    def test_returns_false_when_pdf_empty(self, tmp_path: Path) -> None:
        from mark2tex.app import _pdf_exists_for

        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"")
        assert _pdf_exists_for(str(tmp_path / "doc.md")) is False


# ---------------------------------------------------------------------------
# _log_console
# ---------------------------------------------------------------------------


class TestLogConsole:
    def test_appends_to_console_lines(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        Mark2TeXApp._log_console(app, "hello")
        assert "hello" in app._console_lines

    def test_calls_write_on_richlog(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        Mark2TeXApp._log_console(app, "msg", style="green")
        app.query_one.return_value.write.assert_called_once()


# ---------------------------------------------------------------------------
# _get_selection
# ---------------------------------------------------------------------------


class TestGetSelection:
    def test_returns_tuple_of_three(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.selected_file = "a.md"
        app.selected_template = "tcc-abnt"
        app.selected_font = "times"
        result = Mark2TeXApp._get_selection(app)
        assert result == ("a.md", "tcc-abnt", "times")


# ---------------------------------------------------------------------------
# _apply_template_swap
# ---------------------------------------------------------------------------


class TestApplyTemplateSwap:
    def test_noop_when_no_selected_file(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.selected_file = None
        Mark2TeXApp._apply_template_swap(app, "tcc-abnt")
        app._log_console.assert_not_called()

    def test_noop_when_no_frontmatter(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.selected_file = "doc.md"
        with patch("mark2tex.app.has_frontmatter", return_value=False):
            Mark2TeXApp._apply_template_swap(app, "tcc-abnt")
        app._log_console.assert_not_called()

    def test_logs_success_when_swap_ok(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.selected_file = "doc.md"
        with (
            patch("mark2tex.app.has_frontmatter", return_value=True),
            patch("mark2tex.app.swap_template", return_value=True),
        ):
            Mark2TeXApp._apply_template_swap(app, "dissertacao-abnt")
        app._log_console.assert_called_once()
        app._update_preview.assert_called_once_with("doc.md")

    def test_logs_error_when_swap_fails(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.selected_file = "doc.md"
        with (
            patch("mark2tex.app.has_frontmatter", return_value=True),
            patch("mark2tex.app.swap_template", return_value=False),
        ):
            Mark2TeXApp._apply_template_swap(app, "artigo-ieee")
        app._log_console.assert_called_once()
        app._update_preview.assert_not_called()


# ---------------------------------------------------------------------------
# on_list_view_selected
# ---------------------------------------------------------------------------


class TestOnListViewSelected:
    def _run(self, app: MagicMock, list_id: str, item: object) -> None:
        from mark2tex.app import Mark2TeXApp

        event = _make_event(list_id, item)
        with _isinstance_patch("OptionItem"), _isinstance_patch("FontItem"), _isinstance_patch("DirItem"):
            Mark2TeXApp.on_list_view_selected(app, event)

    def _run_typed(self, app: MagicMock, list_id: str, item: object, cls_name: str) -> None:
        """Run with isinstance returning True only for the given class name."""
        import builtins

        from mark2tex.app import Mark2TeXApp
        real = builtins.isinstance

        def _fake(obj: object, cls: object) -> bool:  # noqa: ANN401
            import mark2tex.app as _a
            target = getattr(_a, cls_name, None)
            if target is not None and cls is target and obj is item:
                return True
            if isinstance(cls, tuple):
                return any(_fake(obj, c) for c in cls)
            return real(obj, cls)  # type: ignore[arg-type]

        event = _make_event(list_id, item)
        with patch("mark2tex.app.isinstance", side_effect=_fake):
            Mark2TeXApp.on_list_view_selected(app, event)

    def test_file_list_option_sets_selected_file(self) -> None:
        app = _make_app()
        item = _option("thesis.md")
        self._run_typed(app, "file-list", item, "OptionItem")
        assert app.selected_file == "thesis.md"

    def test_template_list_sets_selected_template_and_swaps(self) -> None:
        app = _make_app()
        item = _option("dissertacao-abnt")
        self._run_typed(app, "template-list", item, "OptionItem")
        assert app.selected_template == "dissertacao-abnt"
        app._apply_template_swap.assert_called_once_with("dissertacao-abnt")

    def test_font_list_sets_selected_font(self) -> None:
        app = _make_app()
        item = _font_item("times", "Liberation Serif (Times)")
        self._run_typed(app, "font-list", item, "FontItem")
        assert app.selected_font == "times"

    def test_file_list_dir_item_navigates(self) -> None:
        app = _make_app()
        target = Path("/some/dir")
        item = _dir_item(target)
        self._run_typed(app, "file-list", item, "DirItem")
        app._navigate_to.assert_called_once_with(target)


# ---------------------------------------------------------------------------
# on_list_view_highlighted  (template-list + file-list + font-list)
# ---------------------------------------------------------------------------


class TestHighlightedTemplateLabel:
    """on_list_view_highlighted — template-list branch must update the status
    label without calling ``_apply_template_swap`` or mutating
    ``self.selected_template``."""

    def _run(self, app: MagicMock, label_text: str) -> None:
        import builtins

        from mark2tex.app import Mark2TeXApp, OptionItem

        event = _make_event("template-list", SimpleNamespace(label_text=label_text))
        real = builtins.isinstance

        def _isinstance(obj: object, cls: object) -> bool:  # noqa: ANN401
            if cls is OptionItem:
                return True
            return real(obj, cls)  # type: ignore[arg-type]

        with patch("mark2tex.app.isinstance", side_effect=_isinstance):
            Mark2TeXApp.on_list_view_highlighted(app, event)

    def test_label_updated(self) -> None:
        app = _make_app()
        self._run(app, "dissertacao-abnt")
        app.query_one.return_value.update.assert_called_once_with("Template : dissertacao-abnt")

    def test_apply_template_swap_not_called(self) -> None:
        app = _make_app()
        self._run(app, "artigo-ieee")
        app._apply_template_swap.assert_not_called()

    def test_selected_template_not_mutated(self) -> None:
        app = _make_app()
        app.selected_template = "tcc-abnt"
        self._run(app, "artigo-acm")
        assert app.selected_template == "tcc-abnt"


class TestHighlightedFileList:
    """on_list_view_highlighted — file-list OptionItem branch."""

    def _run(self, app: MagicMock, filename: str) -> None:
        import builtins

        from mark2tex.app import Mark2TeXApp, OptionItem

        item = SimpleNamespace(label_text=filename)
        event = _make_event("file-list", item)
        real = builtins.isinstance

        def _isinstance(obj: object, cls: object) -> bool:  # noqa: ANN401
            if cls is OptionItem and obj is item:
                return True
            return real(obj, cls)  # type: ignore[arg-type]

        with patch("mark2tex.app.isinstance", side_effect=_isinstance):
            Mark2TeXApp.on_list_view_highlighted(app, event)

    def test_selected_file_updated(self) -> None:
        app = _make_app()
        self._run(app, "paper.md")
        assert app.selected_file == "paper.md"

    def test_preview_refreshed(self) -> None:
        app = _make_app()
        self._run(app, "paper.md")
        app._update_preview.assert_called_once_with("paper.md")

    def test_info_tab_reset(self) -> None:
        app = _make_app()
        self._run(app, "paper.md")
        app._reset_info_tab.assert_called_once()


class TestHighlightedFontList:
    """on_list_view_highlighted — font-list branch sets selected_font."""

    def _run(self, app: MagicMock, font_id: str, display_label: str) -> None:
        import builtins

        from mark2tex.app import FontItem, Mark2TeXApp

        item = SimpleNamespace(font_id=font_id, display_label=display_label)
        event = _make_event("font-list", item)
        real = builtins.isinstance

        def _isinstance(obj: object, cls: object) -> bool:  # noqa: ANN401
            if cls is FontItem and obj is item:
                return True
            return real(obj, cls)  # type: ignore[arg-type]

        with patch("mark2tex.app.isinstance", side_effect=_isinstance):
            Mark2TeXApp.on_list_view_highlighted(app, event)

    def test_selected_font_set(self) -> None:
        app = _make_app()
        self._run(app, "times", "Liberation Serif (Times)")
        assert app.selected_font == "times"

    def test_status_label_updated(self) -> None:
        app = _make_app()
        self._run(app, "arial", "Liberation Sans (Arial)")
        app.query_one.return_value.update.assert_called_with("Fonte    : Liberation Sans (Arial)")


# ---------------------------------------------------------------------------
# toggle_watch_mode — start branch (template closure) + stop branch
# ---------------------------------------------------------------------------


class TestWatchModeTemplateClosure:
    """Start branch: lambda must read self.selected_template at call time."""

    def _start_watch(self, app: MagicMock, initial_template: str):
        from mark2tex.app import Mark2TeXApp

        app.selected_file = "thesis.md"
        app.selected_template = initial_template
        app.selected_font = None
        app._get_selection.return_value = ("thesis.md", initial_template, None)
        app._current_dir.__truediv__ = lambda _self, _other: MagicMock()

        captured: list = []

        def _fake_start(_abs_file: str, _template: str, callback) -> None:  # noqa: ANN001
            captured.append(callback)

        app.watcher_manager.start_watching.side_effect = _fake_start

        with patch("mark2tex.app.isinstance", side_effect=isinstance):
            Mark2TeXApp.toggle_watch_mode(app)

        assert captured, "start_watching was not called"
        return captured[0]

    def test_lambda_uses_initial_template_when_no_change(self) -> None:
        app = _make_app()
        callback = self._start_watch(app, "tcc-abnt")
        app.selected_template = None
        callback()
        app.compile_specific_document.assert_called_once()
        _, called_template, _ = app.compile_specific_document.call_args[0]
        assert called_template == "tcc-abnt"

    def test_lambda_prefers_updated_selected_template(self) -> None:
        app = _make_app()
        callback = self._start_watch(app, "tcc-abnt")
        app.selected_template = "dissertacao-abnt"
        callback()
        app.compile_specific_document.assert_called_once()
        _, called_template, _ = app.compile_specific_document.call_args[0]
        assert called_template == "dissertacao-abnt"


class TestWatchModeStop:
    """Stop branch: watcher must be stopped and state reset."""

    def test_stop_branch_resets_is_watching(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.is_watching = True
        with patch("mark2tex.app.isinstance", side_effect=isinstance):
            Mark2TeXApp.toggle_watch_mode(app)
        app.watcher_manager.stop_watching.assert_called_once()
        assert app.is_watching is False

    def test_stop_branch_logs_message(self) -> None:
        from mark2tex.app import Mark2TeXApp

        app = _make_app()
        app.is_watching = True
        with patch("mark2tex.app.isinstance", side_effect=isinstance):
            Mark2TeXApp.toggle_watch_mode(app)
        app._log_console.assert_called_once()
