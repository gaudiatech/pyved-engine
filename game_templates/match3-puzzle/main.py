import glvars
import katagames_engine as kengi
kengi.bootstrap_e()  # need to call this asap, in the main file

from config import W, H, FPS
from mymodes import Home, Win, Lose, InGame


pygame = kengi.pygame
GameModeMger = kengi.GameModeMger


class Game:
    def __init__(self):
        self.gmode_manager = GameModeMger.instance()
        self.clock = pygame.time.Clock()

    def run(self):
        kengi.init('custom', screen_dim=(W, H))
        screen = kengi.get_surface()
        self.gmode_manager.register({
            'home': Home('home'),
            'game': InGame('game'),
            'win': Win('win'),
            'lose': Lose('lose'),
        })
        self.gmode_manager.set_curr_mode('home')

        # - game loop
        while not glvars.gameover:
            events = pygame.event.get()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    glvars.gameover = True
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        glvars.gameover = True
            self.gmode_manager.update(events)

            screen.fill('black')
            self.gmode_manager.draw(screen)
            kengi.flip()
            self.clock.tick(FPS)

        kengi.quit()
        print('bye')  # notice that this was a clean exit


if __name__ == '__main__':
    Game().run()
