import pygame
from game import config


class PlayState:
    def __init__(self, app):
        self.app = app
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            from game.states.menu import MenuState
            self.app.set_state(MenuState(self.app))

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(config.BG)
        msg = self.font.render("PLAY (coming soon) - tap to go back", True, config.TEXT)
        surf.blit(msg, msg.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2)))
