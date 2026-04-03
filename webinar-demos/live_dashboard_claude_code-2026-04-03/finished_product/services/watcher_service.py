"""Watch a local Google Drive sync folder for file changes and trigger ETL."""

import logging
import os
import threading
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# File extensions we care about
WATCHED_EXTENSIONS = {".xlsx", ".csv", ".gsheet", ".pdf", ".docx", ".doc", ".txt"}

# Subdirectories that map to object types
WATCHED_SUBDIRS = {"leads", "invoices", "projects"}


class _DebouncedHandler(FileSystemEventHandler):
    """Triggers a sync callback after a 2-second debounce window."""

    def __init__(self, callback, debounce_seconds=2):
        super().__init__()
        self._callback = callback
        self._debounce = debounce_seconds
        self._timer = None
        self._lock = threading.Lock()

    def _schedule_sync(self):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self):
        logger.info("File watcher: debounce elapsed, triggering sync.")
        try:
            self._callback()
        except Exception as e:
            logger.error("File watcher sync failed: %s", e)

    def _is_relevant(self, event):
        if event.is_directory:
            return False
        path = event.src_path
        _, ext = os.path.splitext(path)
        if ext.lower() not in WATCHED_EXTENSIONS:
            return False
        # Check if the file is inside a watched subdirectory
        parts = path.replace("\\", "/").lower().split("/")
        return any(sub in parts for sub in WATCHED_SUBDIRS)

    def on_created(self, event):
        if self._is_relevant(event):
            logger.info("File watcher: detected new file %s", event.src_path)
            self._schedule_sync()

    def on_modified(self, event):
        if self._is_relevant(event):
            logger.info("File watcher: detected modified file %s", event.src_path)
            self._schedule_sync()


class FileWatcher:
    """Watches a directory for spreadsheet changes and triggers ETL."""

    def __init__(self, watch_path, sync_callback):
        self._path = os.path.expanduser(watch_path)
        self._callback = sync_callback
        self._observer = None

    def start(self):
        if not os.path.isdir(self._path):
            logger.warning(
                "File watcher: directory does not exist: %s — skipping.",
                self._path,
            )
            return

        handler = _DebouncedHandler(self._callback)
        self._observer = Observer()
        self._observer.schedule(handler, self._path, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        logger.info("File watcher: monitoring %s", self._path)

    def stop(self):
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            logger.info("File watcher: stopped.")


def start_watcher(watch_path, sync_callback):
    """Convenience function to start the watcher in a background thread."""
    watcher = FileWatcher(watch_path, sync_callback)
    watcher.start()
    return watcher
