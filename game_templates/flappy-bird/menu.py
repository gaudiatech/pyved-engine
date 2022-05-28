import math
import os
import time

import katagames_engine as kengi

from config import SPEED, H, W, ASSETS, IMAGES
from objects import Player, Pipe
from utils import load_image, clamp


pygame = kengi.pygame


class Menu:
    def __init__(self, name, manager: 'MenuManager'):
        self.name = name
        self.manager = manager  # manager from which this class has been referenced

    def update(self, events, dt):
        pass

    def draw(self, surf):
        pass


class HomeScreen(Menu):
    def __init__(self, manager: 'MenuManager'):
        super().__init__('home screen', manager)
        self.message_img = None
        self.bg = None
        self.ground_img = None
        self.ground_offset = 0

    def load_assets(self):
        self.message_img = load_image(os.path.join(IMAGES, 'message.png'), alpha=True, scale=1.5)
        self.bg = load_image(os.path.join(IMAGES, 'bg.png'))
        self.ground_img = load_image(os.path.join(IMAGES, 'base.png'))

    def update(self, events, dt):
        self.ground_offset -= SPEED * dt
        if self.ground_offset < -self.ground_img.get_width():
            self.ground_offset = 0
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:  # left click
                    self.manager.switch_mode('game', reset=True)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        for i in range(4):
            surf.blit(self.ground_img, (i * self.ground_img.get_width() + self.ground_offset, H - 50))
        surf.blit(self.message_img,
                  self.message_img.get_rect(center=(
                      W // 2, H // 2 + 5 * math.sin(time.time() * 5)
                  )))


class Game(Menu):
    def __init__(self, manager: 'MenuManager'):
        super().__init__('game', manager)

        # for assets
        self.bg = None
        self.ground_img = None
        self.game_over_msg = None

        self.score_img = None
        self.numbers = None
        self.font = None
        self.pipes = None
        self.player = None

        self.show_score = False
        self.ground_offset = 0
        self.speed = SPEED
        self.stopped = False
        self.score = 0
        self.pipe_spawner = 0
        self.pipe_spawn_distances = {
            2: 200,
            3: 225,
            4: 250,
            5: 250,
            6: 275,
            7: 275,
            8: 275,
            9: 300,
            10: 300
        }
        self.original_speed = self.speed

    def load_assets(self):
        self.player = Player()
        self.pipes = [Pipe(W // 2 + i * 200) for i in range(5)]

        self.bg = load_image(os.path.join(IMAGES, 'bg.png'))
        self.ground_img = load_image(os.path.join(IMAGES, 'base.png'))
        self.game_over_msg = load_image(os.path.join(IMAGES, 'gameover.png'), alpha=True, scale=1.5)

        self.score_img = load_image(os.path.join(IMAGES, 'score.png'), alpha=True)
        self.numbers = {i: load_image(os.path.join(IMAGES, f'{i}.png'), alpha=True) for i in range(10)}
        self.font = pygame.font.Font(os.path.join(ASSETS, 'flappy bird font.ttf'), 20)

    def stop_game(self):
        if self.stopped:
            return
        self.speed = 0
        if self.player.dy < 0:
            self.player.dy = 0
        self.stopped = True
        self.player.stopped = True

    def update(self, events, dt):
        player_rect = self.player.rect
        self.pipes = [i for i in self.pipes if i.visible]
        if not self.stopped:
            self.original_speed += 0.0005 * dt
            self.original_speed = clamp(self.original_speed, SPEED, 10)
            self.speed = round(self.original_speed, 2)
            self.ground_offset -= self.speed * dt
            self.pipe_spawner -= self.speed * dt
            if self.pipe_spawner < -self.pipe_spawn_distances[round(self.speed)]:
                self.pipe_spawner = 0
                self.pipes.append(Pipe(self.pipes[-1].x + self.pipe_spawn_distances[round(self.speed)]))
            if self.ground_offset < -self.ground_img.get_width():
                self.ground_offset = 0
            for i in self.pipes:
                i.move(self.speed, dt)
                if i.x < self.player.x - 100:
                    if not i.scored:
                        self.score += 1
                        i.scored = True
                if i.x < -i.image.get_width():
                    i.visible = False
                if i.collision(player_rect):
                    self.stop_game()
        self.player.update(events, dt)
        if player_rect.top < 0:
            self.stop_game()
        if player_rect.bottom > H - 50:
            self.stop_game()
            self.show_score = True
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.show_score:
                        self.manager.switch_mode('home')

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        for i in range(4):
            surf.blit(self.ground_img, (i * self.ground_img.get_width() + round(self.ground_offset), H - 50))
        for i in self.pipes:
            i.draw(surf)
        self.player.draw(surf)

        # generate score image
        w, h = self.numbers[0].get_size()
        score = str(self.score)
        s = pygame.Surface((w * len(score), h), pygame.SRCALPHA)
        for i in range(len(score)):
            s.blit(self.numbers[int(score[i])], (i * w, 0))
        if self.show_score:
            surf.blit(
                self.game_over_msg, self.game_over_msg.get_rect(center=(W // 2, 150 + 5 * math.sin(time.time() * 5))))
            # pygame.draw.rect(surf, '#DED895', (W // 2 - 100, 250 - 40, 200, 150))
            # pygame.draw.rect(surf, 'brown', (W // 2 - 100, 250 - 40, 200, 150), 3)
            t = self.font.render('click to play again', False, 'white')
            surf.blit(t, t.get_rect(center=(W // 2, H - 75 + 10 * math.sin(time.time() * 5))))
            surf.blit(self.score_img, self.score_img.get_rect(center=(W // 2, 250)))
            surf.blit(s, s.get_rect(center=(W // 2, 325)))
        else:
            surf.blit(s, s.get_rect(center=(W // 2, 100)))


class MenuManager:
    def __init__(self):
        self.menus = {
            'home': HomeScreen(self),
            'game': Game(self)
        }
        self._curr_mode = None
        self._curr_mode_obj = None

    def switch_mode(self, mode, reset=False):
        self._curr_mode = mode
        self._curr_mode_obj = self.menus[self._curr_mode]
        if reset:
            self._curr_mode_obj.__init__(self)
            self._curr_mode_obj.load_assets()

    def update(self, events, dt):
        self._curr_mode_obj.update(events, dt)

    def draw(self, surf):
        self._curr_mode_obj.draw(surf)
