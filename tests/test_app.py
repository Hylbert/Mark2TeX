"""Unit tests for Mark2TeXApp behaviour introduced in fix/swap-template-preserves-complex-yaml.

Covers two specific code paths that have no prior test coverage:

1. ``on_list_view_highlighted`` — template-list branch must update the status
   label **without** calling ``_apply_template_swap`` or mutating
   ``self.selected_template``.

2. ``toggle_watch_mode`` — the lambda passed to ``WatcherManager.start_watching``
   must prefer ``self.selected_template`` over the captured ``selected_template``
   so that a template change confirmed with Enter while the watcher is already
   running takes effect on the next auto-recompilation.

These tests exercise the logic through direct method calls with mocked
collaborators, avoiding the full Textual async event-loop setup.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_label_event(list_view_id: str, label_text: str) -> SimpleNamespace:
    """Build a minimal fake ListView.Highlighted event."""
    item = SimpleNamespace(label_text=label_text)
    lv = SimpleNamespace(id=list_view_id)
    return SimpleNamespace(list_view=lv, item=item)


def _make_app() -> MagicMock:
    """Return a MagicMock that stands in for a fully-mounted Mark2TeXApp.

    We intentionally do NOT use ``spec=Mark2TeXApp`` because several attributes
    (``watcher_manager``, ``_current_dir``, ``_console_lines``, etc.) are
    assigned dynamically inside ``on_mount`` and therefore do not appear on the
    class object.  Using ``spec`` would cause ``AttributeError`` for every one
    of those names.  Instead we create a plain MagicMock and set the attributes
    that the tested methods actually read.
    """
    app = MagicMock()
    # Instance attributes set in on_mount
    app.selected_template = None
    app.selected_file = None
    app.selected_font = None
    app.is_watching = False
    app.watcher_manager = MagicMock()
    app._current_dir = MagicMock()
    app._console_lines = []
    return app


# ---------------------------------------------------------------------------
# on_list_view_highlighted — template-list branch
# ---------------------------------------------------------------------------


class TestHighlightedTemplateLabel:
    """on_list_view_highlighted must update the status label when the user
    browses the template list, but must NOT call ``_apply_template_swap`` and
    must NOT mutate ``self.selected_template``."""

    def _run(self, app: MagicMock, label_text: str) -> None:
        """Call the real method body with the mocked app as *self*."""
        import builtins

        from mark2tex.app import Mark2TeXApp, OptionItem

        event = _make_label_event("template-list", label_text)
        real_isinstance = builtins.isinstance

        # OptionItem is a ListItem subclass — isinstance check inside the method
        # requires the item to be a real OptionItem, so we patch isinstance so
        # that our SimpleNamespace item passes the OptionItem check.
        def _isinstance(obj: object, cls: object) -> bool:  # noqa: ANN401
            if cls is OptionItem:
                return True
            return real_isinstance(obj, cls)  # type: ignore[arg-type]

        with patch("mark2tex.app.isinstance", side_effect=_isinstance):
            Mark2TeXApp.on_list_view_highlighted(app, event)

    def test_label_updated(self) -> None:
        app = _make_app()
        self._run(app, "dissertacao-abnt")
        label_mock = app.query_one.return_value
        label_mock.update.assert_called_once_with("Template : dissertacao-abnt")

    def test_apply_template_swap_not_called(self) -> None:
        app = _make_app()
        self._run(app, "artigo-ieee")
        app._apply_template_swap.assert_not_called()

    def test_selected_template_not_mutated(self) -> None:
        app = _make_app()
        app.selected_template = "tcc-abnt"
        self._run(app, "artigo-acm")
        # selected_template must remain unchanged — swap only happens on Enter
        assert app.selected_template == "tcc-abnt"


# ---------------------------------------------------------------------------
# toggle_watch_mode — lambda uses self.selected_template or captured value
# ---------------------------------------------------------------------------


class TestWatchModeTemplateClosure:
    """The lambda passed to ``WatcherManager.start_watching`` must read
    ``self.selected_template`` at call time so that a mid-watch template
    change (confirmed via Enter) is picked up on the next auto-recompilation."""

    def _start_watch(self, app: MagicMock, initial_template: str) -> MagicMock:
        """Call toggle_watch_mode (start branch) and return the captured callback."""
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

        # selected_template unchanged — lambda must fall back to the captured value
        app.selected_template = None
        callback()
        app.compile_specific_document.assert_called_once()
        _, called_template, _ = app.compile_specific_document.call_args[0]
        assert called_template == "tcc-abnt"

    def test_lambda_prefers_updated_selected_template(self) -> None:
        app = _make_app()
        callback = self._start_watch(app, "tcc-abnt")

        # User confirmed a new template with Enter while the watcher was running
        app.selected_template = "dissertacao-abnt"
        callback()
        app.compile_specific_document.assert_called_once()
        _, called_template, _ = app.compile_specific_document.call_args[0]
        assert called_template == "dissertacao-abnt"
