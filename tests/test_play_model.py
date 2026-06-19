import random
from game.maze import generate, farthest_cell, solve
from game.play_model import PlayModel
from game.directions import UP, RIGHT

def _open_dir_from_start(m):
    for d in (RIGHT, (0, 1)):
        if m.can_move((0, 0), d):
            return d
    raise AssertionError("start has no exit")

def test_first_move_starts_timer_and_counts_step():
    m = generate(4, random.Random(1))
    pm = PlayModel(m, (0, 0), farthest_cell(m, (0, 0)))
    pm.try_step(_open_dir_from_start(m), now_ms=1000)
    assert pm.start_time == 1000
    assert pm.steps == 1

def test_blocked_move_does_nothing():
    m = generate(4, random.Random(1))
    pm = PlayModel(m, (0, 0), farthest_cell(m, (0, 0)))
    assert pm.try_step(UP, now_ms=500) is False
    assert pm.steps == 0
    assert pm.start_time is None

def test_reaching_goal_wins_and_stops_timer():
    m = generate(3, random.Random(5))
    goal = farthest_cell(m, (0, 0))
    path = solve(m, (0, 0), goal)
    pm = PlayModel(m, (0, 0), goal)
    t = 0
    for i in range(1, len(path)):
        d = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        t += 100
        pm.try_step(d, now_ms=t)
    assert pm.won is True
    assert pm.end_time == t
    assert pm.steps == len(path) - 1
    assert pm.try_step(RIGHT, now_ms=t + 100) is False  # ignored after win

def test_elapsed_freezes_after_win():
    m = generate(3, random.Random(5))
    goal = farthest_cell(m, (0, 0))
    path = solve(m, (0, 0), goal)
    pm = PlayModel(m, (0, 0), goal)
    t = 0
    for i in range(1, len(path)):
        d = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        t += 100
        pm.try_step(d, now_ms=t)
    assert pm.elapsed_ms(now_ms=t + 9999) == pm.end_time - pm.start_time
