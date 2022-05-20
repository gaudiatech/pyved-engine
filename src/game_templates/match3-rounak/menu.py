import sys

import pygame.display

from utils import text
from objects import Puzzle
from ui import Button
from config import W, H


class Menu:
    """
    Base signature for all menus
    """

    def __init__(self, manager: 'MenuManager', name='menu'):
        self.manager = manager
        self.name = name

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.blit(text(self.name, aliased=True), (50, 50))


class Home(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.buttons = [
            Button(W // 2 - 100, H // 2, 200, 50, 'Play', action=lambda: self.manager.switch_mode('game', reset=True)),
            Button(W // 2 - 100, H // 2 + 100, 200, 50, 'Exit', action=sys.exit)
        ]
        self.text = text('Match-3 Puzzle!', aliased=True)

    def update(self, events: list[pygame.event.Event]):
        for i in self.buttons:
            i.update(events)

    def draw(self, surf: pygame.Surface):
        for i in self.buttons:
            i.draw(surf)
        surf.blit(self.text, self.text.get_rect(center=(W // 2, H // 2 - 150)))


class Game(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.puzzle = Puzzle()
        self.puzzle.init_puzzle()
        self.over = ''

    def update(self, events: list[pygame.event.Event]):
        puzzle = self.puzzle
        self.puzzle.update(events)
        if self.over:
            self.manager.switch_mode(self.over, reset=True)
        if puzzle.over:
            if puzzle.score < puzzle.target_score:
                self.over = 'lose'
            else:
                self.over = 'win'

    def draw(self, surf: pygame.Surface):
        self.puzzle.draw(surf)


class Win(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.buttons = [
            Button(W // 2 - 100, H // 2, 200, 50, 'Home', action=lambda: self.manager.switch_mode('home', reset=True)),
            Button(W // 2 - 100, H // 2 + 100, 200, 50, 'Exit', action=sys.exit)
        ]
        self.text = text('You Won!', aliased=True)
        self.screen = pygame.display.get_surface().copy()
        self.bg = pygame.Surface(self.screen.get_size()).convert_alpha()
        self.alpha = 0
        self.bg.set_alpha(self.alpha)

    def update(self, events: list[pygame.event.Event]):
        for i in self.buttons:
            i.update(events)
        if self.alpha < 200:
            self.alpha += 10
        self.bg.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface):
        surf.blit(self.screen, (0, 0))
        surf.blit(self.bg, (0, 0))
        for i in self.buttons:
            i.draw(surf)
        surf.blit(self.text, self.text.get_rect(center=(W // 2, H // 2 - 150)))


class Lose(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        self.buttons = [
            Button(W // 2 - 100, H // 2, 200, 50, 'Replay', action=lambda: self.manager.switch_mode('game', reset=True)),
            Button(W // 2 - 100, H // 2 + 100, 200, 50, 'Home', action=lambda: self.manager.switch_mode('home', reset=True))
        ]
        self.text = text('You Lost!', aliased=True)
        self.screen = pygame.display.get_surface().copy()
        self.bg = pygame.Surface(self.screen.get_size()).convert_alpha()
        self.alpha = 0
        self.bg.set_alpha(self.alpha)

    def update(self, events: list[pygame.event.Event]):
        for i in self.buttons:
            i.update(events)
        if self.alpha < 200:
            self.alpha += 10
        self.bg.set_alpha(self.alpha)

    def draw(self, surf: pygame.Surface):
        surf.blit(self.screen, (0, 0))
        surf.blit(self.bg, (0, 0))
        for i in self.buttons:
            i.draw(surf)
        surf.blit(self.text, self.text.get_rect(center=(W // 2, H // 2 - 150)))


class MenuManager:
    def __init__(self):
        self.menus = {
            'home': Home(self, 'home'),
            'game': Game(self, 'game'),
            'win': Win(self, 'win'),
            'lose': Lose(self, 'lose'),
        }
        self.mode = 'home'
        self.menu = self.menus[self.mode]

    def switch_mode(self, mode, reset=False):
        if mode in self.menus:
            self.mode = mode
            self.menu = self.menus[self.mode]
            if reset:
                self.menu.__init__(self, self.menu.name)

    def update(self, events: list[pygame.event.Event]):
        self.menu.update(events)

    def draw(self, surf: pygame.Surface):
        self.menu.draw(surf)
