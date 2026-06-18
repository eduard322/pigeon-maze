import random
from collections import deque

from game.directions import DIRS, UP, DOWN, LEFT, RIGHT  # noqa: F401 (re-exported)


class Maze:
    def __init__(self, n, walls):
        self.n = n
        self.walls = walls  # (2n+1) x (2n+1) list[bytearray]

    def can_move(self, cell, direction):
        cx, cy = cell
        dx, dy = direction
        nx, ny = cx + dx, cy + dy
        if not (0 <= nx < self.n and 0 <= ny < self.n):
            return False
        return self.walls[2 * cy + 1 + dy][2 * cx + 1 + dx] == 0


def generate(n, rng=None):
    rng = rng or random.Random()
    size = 2 * n + 1
    walls = [bytearray([1]) * size for _ in range(size)]
    visited = [[False] * n for _ in range(n)]
    stack = [(0, 0)]
    visited[0][0] = True
    walls[1][1] = 0
    while stack:
        cx, cy = stack[-1]
        neighbours = []
        for dx, dy in DIRS:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < n and 0 <= ny < n and not visited[ny][nx]:
                neighbours.append((dx, dy, nx, ny))
        if not neighbours:
            stack.pop()
            continue
        dx, dy, nx, ny = rng.choice(neighbours)
        visited[ny][nx] = True
        walls[2 * cy + 1 + dy][2 * cx + 1 + dx] = 0  # wall between cells
        walls[2 * ny + 1][2 * nx + 1] = 0            # neighbour cell center
        stack.append((nx, ny))
    return Maze(n, walls)


def bfs(maze, start):
    dist = {start: 0}
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for dx, dy in DIRS:
            if maze.can_move(cur, (dx, dy)):
                nb = (cur[0] + dx, cur[1] + dy)
                if nb not in dist:
                    dist[nb] = dist[cur] + 1
                    prev[nb] = cur
                    queue.append(nb)
    return dist, prev
