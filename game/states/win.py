import pygame

from game import config
from game.pigeon import slice_sheet, Anim
from game.stats import efficiency, format_time


class WinState:
    def __init__(self, app, model, optimal, goal, maze):
        self.app = app
        self.model = model
        self.optimal = optimal
        self.goal = goal
        self.maze = maze
        sheet = pygame.image.load(config.ASSET_PECK).convert_alpha()
        self.peck = Anim(slice_sheet(sheet, *config.PECK_FRAME), config.PECK_FPS)
        self.peck_scale = 3 * config.S
        self.font = pygame.font.SysFont("monospace", config.FONT_UI, bold=True)
        self.big = pygame.font.SysFont("monospace", config.FONT_BIG, bold=True)

        # Buttons anchored from the bottom so the layout fits any screen height.
        bw, bh = 200 * config.S, 50 * config.S
        self.menu_rect = pygame.Rect(0, 0, bw, bh)
        self.menu_rect.center = (config.WIDTH // 2, config.HEIGHT - 44 * config.S)
        self.repeat_rect = pygame.Rect(0, 0, bw, bh)
        self.repeat_rect.center = (config.WIDTH // 2, config.HEIGHT - 104 * config.S)

        self.elapsed = model.elapsed_ms(pygame.time.get_ticks())
        self.eff = efficiency(optimal, model.steps)
        self.improved_time, self.improved_eff = app.best.record(self.elapsed, self.eff)
        self.lines = [
            f"Time   {format_time(self.elapsed)}",
            f"Steps  {model.steps}  (best {optimal})",
            f"Route  {int(round(self.eff * 100))}% efficient",
        ]

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.repeat_rect.collidepoint(event.pos):
                from game.states.play import PlayState
                self.app.set_state(PlayState(self.app))
            elif self.menu_rect.collidepoint(event.pos):
                from game.states.menu import MenuState
                self.app.set_state(MenuState(self.app))

    def update(self, dt):
        self.peck.update(dt)

    def draw(self, surf):
        s = config.S
        surf.fill(config.BG)
        frame = pygame.transform.scale_by(self.peck.current(), self.peck_scale)
        surf.blit(frame, frame.get_rect(center=(config.WIDTH // 2, 58 * s)))
        title = self.big.render("YOU GOT THE SEEDS!", True, config.TEXT)
        surf.blit(title, title.get_rect(center=(config.WIDTH // 2, 124 * s)))
        y = 168 * s
        for line in self.lines:
            row = self.font.render(line, True, config.TEXT)
            surf.blit(row, row.get_rect(center=(config.WIDTH // 2, y)))
            y += 26 * s
        if self.improved_time or self.improved_eff:
            tag = self.font.render("NEW BEST!", True, config.SEED)
            surf.blit(tag, tag.get_rect(center=(config.WIDTH // 2, y + 6 * s)))
        for rect, text in ((self.repeat_rect, "REPEAT"), (self.menu_rect, "MENU")):
            pygame.draw.rect(surf, config.BUTTON, rect, border_radius=12)
            label = self.font.render(text, True, config.BUTTON_TEXT)
            surf.blit(label, label.get_rect(center=rect.center))
