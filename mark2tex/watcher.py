import logging
import os
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

_logger = logging.getLogger("mark2tex.watcher")

# Directories whose presence in a path indicates the event should be ignored.
_IGNORE_DIRS: frozenset[str] = frozenset({
    ".git", ".venv", ".mypy_cache", "__pycache__", "dist", "build", ".tox",
})

# File suffixes (and trailing characters) associated with editor temp/swap files.
_TEMP_SUFFIXES: frozenset[str] = frozenset({
    ".swp", ".swo", ".tmp", ".bak", ".orig", ".pyc",
})

# Name suffixes that identify ephemeral build artefacts produced by mark2tex
# itself (e.g. thesis._processed.md written by build.sh before pandoc).
# These must never trigger a rebuild — doing so would cause an infinite loop.
_TEMP_NAME_SUFFIXES: frozenset[str] = frozenset({
    "._processed.md",
})


class Mark2TeXWatcher(FileSystemEventHandler):
    def __init__(self, file_to_watch: str, callback, log_path: str = "") -> None:
        self.file_to_watch = os.path.realpath(os.path.abspath(file_to_watch))
        self.callback = callback
        self._last_triggered = 0.0
        self._debounce_interval = 1.5  # raised from 1.0 s — Obsidian writes in two stages

    def _normalize(self, path: str) -> str:
        return os.path.realpath(os.path.abspath(path))

    def _is_temp_file(self, path: str) -> bool:
        """Return True if the path looks like an editor temp/swap file or a
        mark2tex build artefact that must never trigger a rebuild."""
        p = Path(path)
        if p.suffix in _TEMP_SUFFIXES:
            return True
        if p.name.endswith("~"):
            return True
        if any(part in _IGNORE_DIRS for part in p.parts):
            return True
        # Ephemeral copies produced by build.sh (e.g. thesis._processed.md).
        if any(p.name.endswith(s) for s in _TEMP_NAME_SUFFIXES):
            return True
        return False

    def _should_trigger(self, path: str) -> bool:
        if self._is_temp_file(path):
            _logger.debug("watcher: ignoring temp/swap file %s", path)
            return False
        normalized = self._normalize(path)
        match = normalized == self.file_to_watch
        _logger.debug("watcher: event path=%s target=%s match=%s", normalized, self.file_to_watch, match)
        return match

    def _trigger(self) -> None:
        current_time = time.time()
        if current_time - self._last_triggered > self._debounce_interval:
            self._last_triggered = current_time
            _logger.debug("watcher: callback triggered")
            self.callback()
        else:
            _logger.debug("watcher: callback suppressed by debounce")

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        if self._should_trigger(event.src_path):
            self._trigger()

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        if self._should_trigger(event.src_path):
            self._trigger()

    def on_moved(self, event) -> None:
        if event.is_directory:
            return
        dest_path = getattr(event, "dest_path", "")
        if self._should_trigger(event.src_path) or (dest_path and self._should_trigger(dest_path)):
            self._trigger()


class WatcherManager:
    def __init__(self) -> None:
        self.observer: BaseObserver | None      = None
        self.thread:   threading.Thread | None  = None

    def start_watching(self, file_path: str, template: str, compile_callback) -> None:
        self.stop_watching()

        watch_dir = os.path.dirname(os.path.realpath(os.path.abspath(file_path)))
        event_handler = Mark2TeXWatcher(file_path, compile_callback)

        self.observer = Observer()
        self.observer.schedule(event_handler, path=watch_dir, recursive=False)
        self.observer.start()

        self.thread = threading.Thread(target=self.observer.join, daemon=True)
        self.thread.start()

    def stop_watching(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=1.0)
            self.observer = None

        self.thread = None
