"""Unit tests for mark2tex.watcher.

All filesystem and Observer calls are mocked so tests run without
a real watchdog daemon or disk access.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mark2tex.watcher import (
    _IGNORE_DIRS,
    _TEMP_NAME_SUFFIXES,
    _TEMP_SUFFIXES,
    Mark2TeXWatcher,
    WatcherManager,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_watcher(tmp_path: Path) -> tuple[Mark2TeXWatcher, MagicMock]:
    """Return a watcher pointed at a real temp file and a mock callback."""
    target = tmp_path / "document.md"
    target.write_text("# Hello")
    callback = MagicMock()
    return Mark2TeXWatcher(str(target), callback), callback


def _file_event(path: str, is_directory: bool = False) -> MagicMock:
    event = MagicMock()
    event.src_path = path
    event.is_directory = is_directory
    return event


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

def test_temp_suffixes_contains_common_editors():
    for suffix in (".swp", ".swo", ".tmp", ".bak", ".orig"):
        assert suffix in _TEMP_SUFFIXES


def test_ignore_dirs_contains_common_dirs():
    for d in (".git", ".venv", "__pycache__", "dist", "build"):
        assert d in _IGNORE_DIRS


def test_temp_name_suffixes_contains_processed_md() -> None:
    """_TEMP_NAME_SUFFIXES must declare the ephemeral build artefact suffix."""
    assert "._processed.md" in _TEMP_NAME_SUFFIXES


# ---------------------------------------------------------------------------
# _is_temp_file
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", [
    "/home/user/doc.md.swp",
    "/home/user/doc.md.swo",
    "/home/user/doc.md.tmp",
    "/home/user/doc.md.bak",
    "/home/user/doc.md.orig",
    "/home/user/doc.md~",
])
def test_is_temp_file_returns_true_for_temp_suffixes(filename, tmp_path):
    watcher = Mark2TeXWatcher(str(tmp_path / "document.md"), MagicMock())
    assert watcher._is_temp_file(filename) is True


@pytest.mark.parametrize("path", [
    "/project/.git/COMMIT_EDITMSG",
    "/project/.venv/lib/python3.11/site-packages/foo.py",
    "/project/__pycache__/app.cpython-311.pyc",
    "/project/dist/mark2tex-0.2.2.tar.gz",
    "/project/build/output.pdf",
])
def test_is_temp_file_returns_true_for_ignored_dirs(path, tmp_path):
    watcher = Mark2TeXWatcher(str(tmp_path / "document.md"), MagicMock())
    assert watcher._is_temp_file(path) is True


def test_is_temp_file_returns_false_for_normal_md(tmp_path):
    target = tmp_path / "document.md"
    watcher = Mark2TeXWatcher(str(target), MagicMock())
    assert watcher._is_temp_file(str(target)) is False


@pytest.mark.parametrize("filename", [
    "/home/user/thesis._processed.md",
    "/project/docs/chapter1._processed.md",
    "/tmp/output._processed.md",
])
def test_is_temp_file_returns_true_for_processed_md_artefact(filename, tmp_path) -> None:
    """._processed.md copies written by build.sh must be classified as temp files."""
    watcher = Mark2TeXWatcher(str(tmp_path / "document.md"), MagicMock())
    assert watcher._is_temp_file(filename) is True


def test_processed_md_does_not_trigger_callback(tmp_path) -> None:
    """A watchdog event for a ._processed.md path must never invoke the rebuild callback."""
    watcher, callback = _make_watcher(tmp_path)
    artefact = str(tmp_path / "document._processed.md")
    watcher.on_modified(_file_event(artefact))
    watcher.on_created(_file_event(artefact))
    callback.assert_not_called()


# ---------------------------------------------------------------------------
# _should_trigger
# ---------------------------------------------------------------------------

def test_should_trigger_true_for_watched_file(tmp_path):
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(watcher.file_to_watch) is True


def test_should_trigger_false_for_swap_file(tmp_path):
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(str(tmp_path / "document.md.swp")) is False


def test_should_trigger_false_for_tilde_file(tmp_path):
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(str(tmp_path / "document.md~")) is False


def test_should_trigger_false_for_unrelated_md(tmp_path):
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(str(tmp_path / "other.md")) is False


def test_should_trigger_false_for_git_path(tmp_path):
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(str(tmp_path / ".git" / "index")) is False


def test_should_trigger_false_for_processed_md(tmp_path) -> None:
    """_should_trigger must return False for ._processed.md artefacts."""
    watcher, _ = _make_watcher(tmp_path)
    assert watcher._should_trigger(str(tmp_path / "document._processed.md")) is False


# ---------------------------------------------------------------------------
# on_modified / on_created / on_moved
# ---------------------------------------------------------------------------

def test_on_modified_triggers_callback_for_watched_file(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher.on_modified(_file_event(watcher.file_to_watch))
    callback.assert_called_once()


def test_on_modified_ignores_swap_file(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher.on_modified(_file_event(str(tmp_path / "document.md.swp")))
    callback.assert_not_called()


def test_on_modified_ignores_directory_events(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher.on_modified(_file_event(watcher.file_to_watch, is_directory=True))
    callback.assert_not_called()


def test_on_created_triggers_callback_for_watched_file(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher.on_created(_file_event(watcher.file_to_watch))
    callback.assert_called_once()


def test_on_moved_triggers_callback_when_dest_matches(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    event = MagicMock()
    event.is_directory = False
    event.src_path = str(tmp_path / "other.md")
    event.dest_path = watcher.file_to_watch
    watcher.on_moved(event)
    callback.assert_called_once()


# ---------------------------------------------------------------------------
# Debounce
# ---------------------------------------------------------------------------

def test_debounce_suppresses_rapid_second_event(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher._debounce_interval = 10.0
    event = _file_event(watcher.file_to_watch)
    watcher.on_modified(event)
    watcher.on_modified(event)
    callback.assert_called_once()


def test_debounce_allows_event_after_interval_expires(tmp_path):
    watcher, callback = _make_watcher(tmp_path)
    watcher._debounce_interval = 0.0
    event = _file_event(watcher.file_to_watch)
    watcher.on_modified(event)
    watcher.on_modified(event)
    assert callback.call_count == 2


# ---------------------------------------------------------------------------
# WatcherManager lifecycle
# ---------------------------------------------------------------------------

def test_watcher_manager_stop_watching_is_idempotent():
    """stop_watching() must not raise when called with no observer set."""
    wm = WatcherManager()
    wm.stop_watching()


@patch("mark2tex.watcher.Observer")
def test_watcher_manager_starts_observer(mock_observer_cls, tmp_path):
    target = tmp_path / "doc.md"
    target.write_text("# test")
    mock_obs = MagicMock()
    mock_observer_cls.return_value = mock_obs

    wm = WatcherManager()
    wm.start_watching(str(target), "tcc-abnt", MagicMock())

    mock_obs.schedule.assert_called_once()
    mock_obs.start.assert_called_once()


@patch("mark2tex.watcher.Observer")
def test_watcher_manager_stop_calls_observer_stop(mock_observer_cls, tmp_path):
    target = tmp_path / "doc.md"
    target.write_text("# test")
    mock_obs = MagicMock()
    mock_observer_cls.return_value = mock_obs

    wm = WatcherManager()
    wm.start_watching(str(target), "tcc-abnt", MagicMock())
    wm.stop_watching()

    mock_obs.stop.assert_called_once()


@patch("mark2tex.watcher.Observer")
def test_watcher_manager_restart_stops_previous_observer(mock_observer_cls, tmp_path):
    """start_watching() called twice must stop the first observer before starting a new one."""
    target = tmp_path / "doc.md"
    target.write_text("# test")
    mock_obs = MagicMock()
    mock_observer_cls.return_value = mock_obs

    wm = WatcherManager()
    wm.start_watching(str(target), "tcc-abnt", MagicMock())
    wm.start_watching(str(target), "tcc-abnt", MagicMock())

    assert mock_obs.stop.call_count >= 1


# ---------------------------------------------------------------------------
# Regression guard: legacy _log() must not exist
# ---------------------------------------------------------------------------

def test_watcher_has_no_legacy_log_method(tmp_path):
    """The old _log() that wrote unconditionally to disk must not exist."""
    watcher = Mark2TeXWatcher(str(tmp_path / "document.md"), MagicMock())
    assert not hasattr(watcher, "_log"), (
        "_log() still present — replace with logging.getLogger"
    )
