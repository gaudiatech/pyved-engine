import sys
import pygame

from config import W, H, FPS
from menu import MenuManager

pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))  # , pygame.SCALED | pygame.FULLSCREEN)
        self.manager = MenuManager()
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        sys.exit(0)
            self.manager.update(events)
            self.screen.fill('black')
            self.manager.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)
            # print(self.clock.get_fps())


if __name__ == '__main__':
    Game().run()
