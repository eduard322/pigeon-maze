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


from game.maze import farthest_cell, solve, step
from game.directions import RIGHT, DOWN

def test_farthest_cell_has_max_distance():
    m = generate(7, random.Random(3))
    dist, _ = bfs(m, (0, 0))
    far = farthest_cell(m, (0, 0))
    assert dist[far] == max(dist.values())

def test_solve_path_matches_bfs_distance():
    m = generate(7, random.Random(3))
    goal = farthest_cell(m, (0, 0))
    path = solve(m, (0, 0), goal)
    dist, _ = bfs(m, (0, 0))
    assert path[0] == (0, 0)
    assert path[-1] == goal
    assert len(path) - 1 == dist[goal]

def test_step_blocked_returns_same_cell():
    m = generate(4, random.Random(1))
    assert step(m, (0, 0), UP) == (0, 0)

def test_step_moves_when_open():
    m = generate(4, random.Random(1))
    moved = step(m, (0, 0), RIGHT) != (0, 0) or step(m, (0, 0), DOWN) != (0, 0)
    assert moved
