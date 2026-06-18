import pygame
from game import config
from game.pigeon import slice_sheet


class MenuState:
    def __init__(self, app):
        self.app = app
        self.title_font = pygame.font.SysFont("monospace", 40, bold=True)
        self.font = pygame.font.SysFont("monospace", 20, bold=True)
        sheet = pygame.image.load(config.ASSET_WALK).convert_alpha()
        self.pigeon = slice_sheet(sheet, *config.WALK_FRAME)[0]
        self.pigeon = pygame.transform.scale_by(self.pigeon, 3)
        self.play_rect = pygame.Rect(0, 0, 200, 56)
        self.play_rect.center = (config.WIDTH // 2, config.HEIGHT // 2 + 120)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.play_rect.collidepoint(event.pos):
            from game.states.play import PlayState
            self.app.set_state(PlayState(self.app))

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(config.BG)
        title = self.title_font.render("PIGEON MAZE", True, config.TEXT)
        surf.blit(title, title.get_rect(center=(config.WIDTH // 2, 140)))
        rect = self.pigeon.get_rect(center=(config.WIDTH // 2, 240))
        surf.blit(self.pigeon, rect)
        pygame.draw.rect(surf, config.BUTTON, self.play_rect, border_radius=12)
        label = self.font.render("PLAY", True, config.BUTTON_TEXT)
        surf.blit(label, label.get_rect(center=self.play_rect.center))
        best = self.app.best.summary_line()
        if best:
            line = self.font.render(best, True, config.TEXT_DIM)
            surf.blit(line, line.get_rect(center=(config.WIDTH // 2, config.HEIGHT - 60)))
