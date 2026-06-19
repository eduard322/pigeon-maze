def efficiency(optimal, steps):
    """Fraction of moves that were useful (1.0 = no wasted steps)."""
    if steps <= 0:
        return 0.0
    return min(1.0, optimal / steps)


def format_time(ms):
    total_seconds = ms / 1000.0
    minutes = int(total_seconds // 60)
    seconds = total_seconds - 60 * minutes
    return f"{minutes:01d}:{seconds:05.2f}"
