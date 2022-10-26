import glvars
import katagames_engine as kengi
from config import W, H
from objects import Puzzle


pygame = kengi.pygame
drawtext = kengi.util.drawtext
Button = kengi.tankui.Button

def sig_endgame():
    glvars.gameover = True


class Home(kengi.BaseGameMode):
    def __init__(self, name):
        super().__init__(name)
        self.buttons = [
            Button(W // 2 - 100, H // 2, 200, 50, 'Play', action=lambda: self._manager.switch_mode('game', reset=True)),
            Button(W // 2 - 100, H // 2 + 100, 200, 50, 'Exit', action=sig_endgame)
        ]
        self.text = drawtext('Match-3 Puzzle!', aliased=True)

    def update(self, events):
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                glvars.gameover = True
        for i in self.buttons:
            i.update(events)

    def draw(self, surf):
        for i in self.buttons:
            i.draw(surf)
        surf.blit(self.text, self.text.get_rect(center=(W // 2, H // 2 - 150)))


class InGame(kengi.BaseGameMode):
    def __init__(self, name):
        super().__init__(name)
        self.puzzle = Puzzle()
        self.puzzle.init_puzzle()
        self.over = ''

    def update(self, events):  # list[pygame.event.Event]):
        puzzle = self.puzzle
        self.puzzle.update(events)
        if self.over:
            self._manager.switch_mode(self.over, reset=True)
        if puzzle.over:
            if puzzle.score < puzzle.target_score:
                self.over = 'lose'
            else:
                self.over = 'win'

    def draw(self, surf):
        self.puzzle.draw(surf)


class WinOrLooseTemplate(kengi.BaseGameMode):

    def __init__(self, name, buttons, given_text):
        super().__init__(name)
        self.buttons = buttons
        self.text = drawtext(given_text, aliased=True)
        self.screen = pygame.display.get_surface().copy()
        self.bg = pygame.Surface(self.screen.get_size()).convert_alpha()
        self.alpha = 0
        self.bg.set_alpha(self.alpha)

    def update(self, events):
        for i in self.buttons:
            i.update(events)
        if self.alpha < 200:
            self.alpha += 10
        self.bg.set_alpha(self.alpha)

    def draw(self, surf):
        surf.blit(self.screen, (0, 0))
        surf.blit(self.bg, (0, 0))
        for i in self.buttons:
            i.draw(surf)
        surf.blit(self.text, self.text.get_rect(center=(W // 2, H // 2 - 150)))


class Win(WinOrLooseTemplate):

    def __init__(self, name):
        b = [
            Button(
                W // 2 - 100, H // 2, 200, 50,
                'Home', action=lambda: self._manager.switch_mode('home', reset=True)),
            Button(
                W // 2 - 100, H // 2 + 100, 200, 50,
                'Exit', action=sig_endgame)
        ]
        gt = 'You Won!'
        super().__init__(name, b, gt)


class Lose(WinOrLooseTemplate):
    def __init__(self, name):
        b = [
            Button(
                W // 2 - 100, H // 2, 200, 50,
                'Replay', action=lambda: self._manager.switch_mode('game', reset=True)),
            Button(
                W // 2 - 100, H // 2 + 100, 200, 50,
                'Home', action=lambda: self._manager.switch_mode('home', reset=True))
        ]
        gt = 'You Lost!'
        super().__init__(name, b, gt)
