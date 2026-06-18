import asyncio
import pygame

from game import config
from game.web_bridge import init_web, make_storage


class _BestStub:
    def summary_line(self):
        return ""


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Pigeon Maze")
        self.clock = pygame.time.Clock()
        self.storage = make_storage()
        self.best = _BestStub()  # replaced by BestScores in a later task
        from game.states.menu import MenuState
        self.state = MenuState(self)

    def set_state(self, state):
        self.state = state


async def main():
    init_web()
    app = App()
    running = True
    while running:
        dt = app.clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                app.state.handle(event)
        app.state.update(dt)
        app.state.draw(app.screen)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
