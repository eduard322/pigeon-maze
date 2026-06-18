import asyncio
import sys
import textwrap
import traceback

import pygame

from game import config
from game.web_bridge import init_web, make_storage


def _draw_fatal(msg):
    """Render an exception onto the canvas so web errors are visible."""
    print(msg)
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((480, 600))
    screen.fill((20, 20, 24))
    font = pygame.font.Font(None, 22)
    y = 12
    for raw in msg.splitlines()[-26:]:
        for line in (textwrap.wrap(raw, 58) or [""]):
            screen.blit(font.render(line, True, (255, 120, 120)), (8, y))
            y += 22
    pygame.display.flip()


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
    try:
        app = App()
    except Exception:
        _draw_fatal("STARTUP ERROR:\n" + traceback.format_exc())
        while True:
            await asyncio.sleep(0.2)
    running = True
    while running:
        dt = app.clock.tick(config.FPS)
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    app.state.handle(event)
            app.state.update(dt)
            app.state.draw(app.screen)
        except Exception:
            _draw_fatal("RUNTIME ERROR:\n" + traceback.format_exc())
            while True:
                await asyncio.sleep(0.2)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


# Run when launched directly (native) OR under pygbag's web runtime, where the
# module name is not "__main__". Importing on native (tests) stays side-effect free.
if __name__ == "__main__" or sys.platform == "emscripten":
    asyncio.run(main())
