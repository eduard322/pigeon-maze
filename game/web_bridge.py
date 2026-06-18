import sys

IS_WEB = sys.platform == "emscripten"
_window = None


def init_web():
    """Best-effort Telegram WebApp init. Safe to call on native (no-op)."""
    global _window
    if not IS_WEB:
        return
    import platform
    _window = platform.window
    try:
        tg = _window.Telegram.WebApp
        tg.ready()
        tg.expand()
    except Exception:
        pass  # not opened inside Telegram; localStorage still works


class WebStorage:
    """Reads/writes browser localStorage (works in Telegram's webview)."""

    def get(self, key):
        if not IS_WEB or _window is None:
            return None
        value = _window.localStorage.getItem(key)
        return None if value is None else str(value)

    def set(self, key, value):
        if IS_WEB and _window is not None:
            _window.localStorage.setItem(key, str(value))


def make_storage():
    """Pick the right persistence backend for the current platform."""
    if IS_WEB:
        return WebStorage()
    from game.storage import FileStorage
    return FileStorage(".pigeon_scores.json")
