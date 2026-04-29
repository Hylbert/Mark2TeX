import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from docker_manager import DockerManager

class Mark2TeXWatcher(FileSystemEventHandler):
    def __init__(self, file_to_watch, callback):
        self.file_to_watch = os.path.abspath(file_to_watch)
        self.callback = callback
        self._last_triggered = 0
        self._debounce_interval = 1.0  # seconds

    def on_modified(self, event):
        if event.src_path == self.file_to_watch:
            current_time = time.time()
            if current_time - self._last_triggered > self._debounce_interval:
                self._last_triggered = current_time
                self.callback()

class WatcherManager:
    def __init__(self, installation_dir="~/.mark2tex"):
        self.installation_dir = os.path.expanduser(installation_dir)
        self.docker_manager = DockerManager(self.installation_dir)
        self.observer = None
        self.thread = None

    def start_watching(self, file_path, template, compile_callback):
        self.stop_watching()

        event_handler = Mark2TeXWatcher(file_path, compile_callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(file_path)), recursive=False)
        self.observer.start()

        # Run observer in a separate thread to not block TUI
        self.thread = threading.Thread(target=self.observer.join, daemon=True)
        self.thread.start()

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer = None
        if self.thread:
            self.thread.join(timeout=0.1)
            self.thread = None
