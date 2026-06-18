from game.directions import UP, DOWN, LEFT, RIGHT


def tap_direction(pigeon_px, tap_px):
    """Direction (relative to the pigeon) implied by a tap; None if on the pigeon."""
    dx = tap_px[0] - pigeon_px[0]
    dy = tap_px[1] - pigeon_px[1]
    if dx == 0 and dy == 0:
        return None
    if abs(dx) >= abs(dy):
        return RIGHT if dx > 0 else LEFT
    return DOWN if dy > 0 else UP
