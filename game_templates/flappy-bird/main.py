"""

Flappy Bird demo for kengi template
Intended resolution -> 960 X 540
TARGET FPS -> 60 FPS
Delta Time -> Enabled
Code Readability Level -> Beginners / Intermediate

"""
# uncommenting these lines is handy...
# In case you're running the template with no local installation of kengi
import sys
sys.path.append("..\\..")

import katagames_engine as kengi
kengi.init(1, 'Flappy Bird demo with KENGI')
pygame = kengi.pygame


from menu import MenuManager
from config import TARGET_FPS, FPS


screen = None
clock = None


def init_prog():
    global screen, clock
    screen = kengi.get_surface()
    clock = pygame.time.Clock()


def play_game():
    dt = 1  # assuming ratio is 1 initially

    menu_manager = MenuManager()
    # enter first game mode
    menu_manager.switch_mode('home', True)

    while True:
        # global event checking
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return

        # general display blits
        screen.fill('black')

        menu_manager.update(events, dt)
        menu_manager.draw(screen)

        # display update and dt update
        kengi.flip()

        dt = TARGET_FPS * clock.tick(FPS) / 1000  # ratio of target to current FPS
        # dt = round(dt, 6)
        # print(clock.get_fps())
        if dt == 0:
            dt = 1


if __name__ == '__main__':
    init_prog()
    play_game()
    pygame.quit()
