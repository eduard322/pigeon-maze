import random
import pygame

from game import config
from game.maze import generate, farthest_cell, solve, step
from game.input import tap_direction
from game.pigeon import slice_sheet, Anim, should_flip
from game.play_model import PlayModel
from game.stats import format_time
from game.directions import LEFT, RIGHT


class PlayState:
    def __init__(self, app, seed=None):
        self.app = app
        self.maze = generate(config.N, random.Random(seed))
        self.start = (0, 0)
        self.goal = farthest_cell(self.maze, self.start)
        self.model = PlayModel(self.maze, self.start, self.goal)
        self.optimal = len(solve(self.maze, self.start, self.goal)) - 1

        sheet = pygame.image.load(config.ASSET_WALK).convert_alpha()
        frames = slice_sheet(sheet, *config.WALK_FRAME)
        self.walk = Anim(frames, config.WALK_FPS)
        self.standing = frames[0]
        self.scale = config.CELL / config.WALK_FRAME[0] * 1.3

        self.held_dir = None
        self.last_horizontal = RIGHT
        self.moving = False
        self.glide_t = 0.0
        self.maze_origin = (0, config.HUD_H)
        self.from_px = self._cell_center_px(self.model.cell)
        self.to_px = self.from_px

        self.hud_font = pygame.font.SysFont("monospace", 24, bold=True)

    def _cell_center_px(self, cell):
        ox, oy = self.maze_origin
        return (ox + cell[0] * config.CELL + config.CELL / 2,
                oy + cell[1] * config.CELL + config.CELL / 2)

    def _pigeon_screen_px(self):
        if self.moving:
            f = self.glide_t / config.STEP_MS
            return (self.from_px[0] + (self.to_px[0] - self.from_px[0]) * f,
                    self.from_px[1] + (self.to_px[1] - self.from_px[1]) * f)
        return self.to_px

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.held_dir = tap_direction(self._pigeon_screen_px(), event.pos)
            self._try_begin_step()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.held_dir = None

    def _try_begin_step(self):
        if self.moving or self.held_dir is None or self.model.won:
            return
        before = self.model.cell
        moved = self.model.try_step(self.held_dir, pygame.time.get_ticks())
        if not moved:
            return
        if self.held_dir in (LEFT, RIGHT):
            self.last_horizontal = self.held_dir
        self.from_px = self._cell_center_px(before)
        self.to_px = self._cell_center_px(self.model.cell)
        self.moving = True
        self.glide_t = 0.0

    def update(self, dt):
        if self.moving:
            self.glide_t += dt
            self.walk.update(dt)
            if self.glide_t >= config.STEP_MS:
                self.moving = False
                self.glide_t = 0.0
                if self.model.won:
                    from game.states.win import WinState
                    self.app.set_state(
                        WinState(self.app, self.model, self.optimal,
                                 self.goal, self.maze))
                    return
                self._try_begin_step()

    def draw(self, surf):
        surf.fill(config.BG)
        self._draw_maze(surf)
        self._draw_seeds(surf)
        self._draw_pigeon(surf)
        self._draw_hud(surf)

    def _draw_maze(self, surf):
        ox, oy = self.maze_origin
        c = config.CELL
        for cy in range(self.maze.n):
            for cx in range(self.maze.n):
                x, y = ox + cx * c, oy + cy * c
                col = config.PATH if (cx + cy) % 2 == 0 else config.PATH_ALT
                pygame.draw.rect(surf, col, (x, y, c, c))
        t = config.WALL_T
        for cy in range(self.maze.n):
            for cx in range(self.maze.n):
                x, y = ox + cx * c, oy + cy * c
                if not self.maze.can_move((cx, cy), RIGHT):
                    pygame.draw.rect(surf, config.WALL, (x + c - t, y, t, c))
                if not self.maze.can_move((cx, cy), (0, 1)):
                    pygame.draw.rect(surf, config.WALL, (x, y + c - t, c, t))
                if cx == 0 and not self.maze.can_move((cx, cy), LEFT):
                    pygame.draw.rect(surf, config.WALL, (x, y, t, c))
                if cy == 0 and not self.maze.can_move((cx, cy), (0, -1)):
                    pygame.draw.rect(surf, config.WALL, (x, y, c, t))

    def _draw_seeds(self, surf):
        cx, cy = self._cell_center_px(self.goal)
        for dx, dy in [(-4, -2), (2, -4), (5, 0), (-2, 3), (3, 4), (0, 0)]:
            pygame.draw.rect(surf, config.SEED, (cx + dx, cy + dy, 3, 3))

    def _draw_pigeon(self, surf):
        frame = self.walk.current() if self.moving else self.standing
        frame = pygame.transform.scale_by(frame, self.scale)
        if should_flip(self.held_dir, self.last_horizontal):
            frame = pygame.transform.flip(frame, True, False)
        cx, cy = self._pigeon_screen_px()
        surf.blit(frame, frame.get_rect(center=(cx, cy)))

    def _draw_hud(self, surf):
        now = pygame.time.get_ticks()
        text = format_time(self.model.elapsed_ms(now))
        label = self.hud_font.render(text, True, config.TEXT)
        surf.blit(label, (12, 30))
