import random
from game.maze import generate, bfs
from game.directions import LEFT, UP

def test_generate_dimensions():
    m = generate(5, random.Random(1))
    assert m.n == 5
    assert len(m.walls) == 11
    assert all(len(row) == 11 for row in m.walls)

def test_all_cells_reachable():
    m = generate(8, random.Random(2))
    dist, _ = bfs(m, (0, 0))
    assert len(dist) == 8 * 8  # perfect maze: every cell reachable

def test_generate_is_deterministic_with_seed():
    a = generate(6, random.Random(42)).walls
    b = generate(6, random.Random(42)).walls
    assert a == b

def test_cannot_move_out_of_bounds():
    m = generate(4, random.Random(1))
    assert not m.can_move((0, 0), LEFT)
    assert not m.can_move((0, 0), UP)
