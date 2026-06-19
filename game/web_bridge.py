import sys

IS_WEB = sys.platform == "emscripten"
_window = None


def _inject_telegram_sdk():
    """Add the Telegram WebApp SDK <script> to the page (pygbag's HTML omits it)."""
    if getattr(_window, "Telegram", None) is not None:
        return
    doc = _window.document
    script = doc.createElement("script")
    script.src = "https://telegram.org/js/telegram-web-app.js"
    doc.head.appendChild(script)


def init_web():
    """Inject the Telegram SDK and attempt init. Safe to call on native (no-op)."""
    global _window
    if not IS_WEB:
        return
    import platform
    _window = platform.window
    _inject_telegram_sdk()
    apply_telegram()


def apply_telegram():
    """Best-effort ready()/expand()/theme. The injected SDK loads asynchronously,
    so this is retried from the main loop until it succeeds. Returns True once done."""
    if not IS_WEB or _window is None:
        return False
    try:
        tg = _window.Telegram.WebApp
        tg.ready()
        tg.expand()
        bg = tg.themeParams.bg_color
        if bg:
            _window.document.body.style.background = bg
        return True
    except Exception:
        return False  # not in Telegram yet, or SDK still loading


def haptic_success():
    """Fire a Telegram 'success' haptic. No-op outside Telegram/native."""
    if IS_WEB and _window is not None:
        try:
            _window.Telegram.WebApp.HapticFeedback.notificationOccurred("success")
        except Exception:
            pass


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
