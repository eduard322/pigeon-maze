import json
import os


class MemoryStorage:
    """In-memory key/value store (used by tests and as a fallback)."""

    def __init__(self):
        self._d = {}

    def get(self, key):
        return self._d.get(key)

    def set(self, key, value):
        self._d[key] = value


class FileStorage:
    """JSON-file backed store for native runs so scores persist locally."""

    def __init__(self, path):
        self.path = path
        try:
            with open(path) as fh:
                self._d = json.load(fh)
        except (OSError, ValueError):
            self._d = {}

    def get(self, key):
        return self._d.get(key)

    def set(self, key, value):
        self._d[key] = value
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(self._d, fh)
        os.replace(tmp, self.path)
