import pygame

from game import config
from game.pigeon import slice_sheet, Anim


class WinState:
    def __init__(self, app, model, optimal, goal, maze):
        self.app = app
        self.model = model
        self.optimal = optimal
        self.goal = goal
        self.maze = maze
        sheet = pygame.image.load(config.ASSET_PECK).convert_alpha()
        self.peck = Anim(slice_sheet(sheet, *config.PECK_FRAME), config.PECK_FPS)
        self.peck_scale = 4
        self.font = pygame.font.SysFont("monospace", 22, bold=True)
        self.big = pygame.font.SysFont("monospace", 30, bold=True)
        self.repeat_rect = pygame.Rect(0, 0, 180, 52)
        self.menu_rect = pygame.Rect(0, 0, 180, 52)
        self.repeat_rect.center = (config.WIDTH // 2, config.HEIGHT // 2 + 60)
        self.menu_rect.center = (config.WIDTH // 2, config.HEIGHT // 2 + 124)

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
        surf.fill(config.BG)
        frame = pygame.transform.scale_by(self.peck.current(), self.peck_scale)
        surf.blit(frame, frame.get_rect(center=(config.WIDTH // 2, 150)))
        title = self.big.render("YOU GOT THE SEEDS!", True, config.TEXT)
        surf.blit(title, title.get_rect(center=(config.WIDTH // 2, 250)))
        for rect, text in ((self.repeat_rect, "REPEAT"), (self.menu_rect, "MENU")):
            pygame.draw.rect(surf, config.BUTTON, rect, border_radius=12)
            label = self.font.render(text, True, config.BUTTON_TEXT)
            surf.blit(label, label.get_rect(center=rect.center))
