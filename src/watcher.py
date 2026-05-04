import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Mark2TeXWatcher(FileSystemEventHandler):
    def __init__(self, file_to_watch, callback, log_path="tui_console_debug.log"):
        self.file_to_watch = os.path.realpath(os.path.abspath(file_to_watch))
        self.callback = callback
        self.log_path = log_path
        self._last_triggered = 0.0
        self._debounce_interval = 1.0

    def _log(self, message: str) -> None:
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"[WATCHER] {message}\n")
        except Exception:
            pass

    def _normalize(self, path: str) -> str:
        return os.path.realpath(os.path.abspath(path))

    def _should_trigger(self, path: str) -> bool:
        normalized = self._normalize(path)
        match = bool(normalized == self.file_to_watch)
        self._log(f"event path={normalized} target={self.file_to_watch} match={match}")
        return match

    def _trigger(self) -> None:
        current_time = time.time()
        if current_time - self._last_triggered > self._debounce_interval:
            self._last_triggered = current_time
            self._log("callback disparado")
            self.callback()
        else:
            self._log("callback ignorado por debounce")

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
    def __init__(self):
        self.observer = None
        self.thread = None

    def start_watching(self, file_path, template, compile_callback):
        self.stop_watching()

        watch_dir = os.path.dirname(os.path.realpath(os.path.abspath(file_path)))
        event_handler = Mark2TeXWatcher(file_path, compile_callback)

        self.observer = Observer()
        self.observer.schedule(event_handler, path=watch_dir, recursive=False)
        self.observer.start()

        self.thread = threading.Thread(target=self.observer.join, daemon=True)
        self.thread.start()

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=1.0)
            self.observer = None

        self.thread = None