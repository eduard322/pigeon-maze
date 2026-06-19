from game.maze import step


class PlayModel:
    """Headless game state: position, step count, timer, win — no rendering."""

    def __init__(self, maze, start, goal):
        self.maze = maze
        self.cell = start
        self.goal = goal
        self.steps = 0
        self.won = False
        self.start_time = None
        self.end_time = None

    def try_step(self, direction, now_ms):
        if self.won:
            return False
        nxt = step(self.maze, self.cell, direction)
        if nxt == self.cell:
            return False
        if self.start_time is None:
            self.start_time = now_ms
        self.cell = nxt
        self.steps += 1
        if self.cell == self.goal:
            self.won = True
            self.end_time = now_ms
        return True

    def elapsed_ms(self, now_ms):
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else now_ms
        return end - self.start_time
