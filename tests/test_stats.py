from game.stats import efficiency, format_time

def test_efficiency_perfect():
    assert efficiency(10, 10) == 1.0

def test_efficiency_half():
    assert efficiency(10, 20) == 0.5

def test_efficiency_caps_at_one():
    assert efficiency(10, 5) == 1.0

def test_efficiency_zero_steps_is_zero():
    assert efficiency(10, 0) == 0.0

def test_format_time():
    assert format_time(0) == "0:00.00"
    assert format_time(1234) == "0:01.23"
    assert format_time(65000) == "1:05.00"
