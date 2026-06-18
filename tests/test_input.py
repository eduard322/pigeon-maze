from game.input import tap_direction
from game.directions import UP, DOWN, LEFT, RIGHT

def test_tap_right():
    assert tap_direction((100, 100), (160, 110)) == RIGHT

def test_tap_left():
    assert tap_direction((100, 100), (40, 105)) == LEFT

def test_tap_up():
    assert tap_direction((100, 100), (110, 40)) == UP

def test_tap_down():
    assert tap_direction((100, 100), (95, 170)) == DOWN

def test_tap_same_point_returns_none():
    assert tap_direction((100, 100), (100, 100)) is None

def test_diagonal_prefers_dominant_axis():
    assert tap_direction((100, 100), (150, 90)) == RIGHT   # |dx|=50 > |dy|=10
    assert tap_direction((100, 100), (110, 160)) == DOWN   # |dy|=60 > |dx|=10
