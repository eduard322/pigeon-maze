import json
import os

from game.stats import format_time


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


KEY_TIME = "best_time_ms"
KEY_EFF = "best_efficiency"


class BestScores:
    def __init__(self, storage):
        self.storage = storage

    def best_time_ms(self):
        value = self.storage.get(KEY_TIME)
        return int(value) if value is not None else None

    def best_efficiency(self):
        value = self.storage.get(KEY_EFF)
        return float(value) if value is not None else None

    def record(self, time_ms, eff):
        improved_time = False
        improved_eff = False
        best_time = self.best_time_ms()
        if best_time is None or time_ms < best_time:
            self.storage.set(KEY_TIME, str(int(time_ms)))
            improved_time = True
        best_eff = self.best_efficiency()
        if best_eff is None or eff > best_eff:
            self.storage.set(KEY_EFF, str(eff))
            improved_eff = True
        return improved_time, improved_eff

    def summary_line(self):
        bt = self.best_time_ms()
        be = self.best_efficiency()
        if bt is None and be is None:
            return ""
        return f"BEST {format_time(bt)}  ·  {int(round((be or 0) * 100))}%"
