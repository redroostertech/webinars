import json
import os
from datetime import datetime, timezone


class DataRepository:
    """Single responsibility: read and write local JSON data files."""

    def __init__(self, data_dir):
        self._data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _path(self, filename):
        return os.path.join(self._data_dir, filename)

    def read_json(self, filename):
        path = self._path(filename)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return json.load(f)

    def write_json(self, filename, data):
        path = self._path(filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_sync_state(self):
        return self.read_json("sync_state.json")

    def save_sync_state(self, state):
        self.write_json("sync_state.json", state)

    def file_exists(self, filename):
        return os.path.exists(self._path(filename))
