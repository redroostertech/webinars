import json
import os
from datetime import datetime, timezone


class DataRepository:
    """Single responsibility: read and write JSON data files."""

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

    def get_normalized(self):
        return self.read_json("normalized.json")

    def get_sheets_raw(self):
        return self.read_json("sheets_raw.json")

    def get_reddit_raw(self):
        return self.read_json("reddit_raw.json")

    def save_sheets_raw(self, data):
        payload = {
            "headers": data.get("headers", []),
            "rows": data.get("rows", []),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        self.write_json("sheets_raw.json", payload)

    def save_reddit_raw(self, posts):
        self.write_json("reddit_raw.json", posts)

    def save_normalized(self, sheets_data, reddit_data):
        payload = {
            "sheets_data": sheets_data,
            "reddit_data": reddit_data,
            "metadata": {
                "sheets_count": len(sheets_data),
                "reddit_count": len(reddit_data),
                "normalized_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        self.write_json("normalized.json", payload)

    def file_exists(self, filename):
        return os.path.exists(self._path(filename))
