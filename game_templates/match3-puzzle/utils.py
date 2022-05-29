import math
import time
from functools import lru_cache
from typing import Literal

import pygame


def clamp(value, mini, maxi):
    """Clamp value between mini and maxi"""
    if value < mini:
        return mini
    elif maxi < value:
        return maxi
    else:
        return value


def distance(p1, p2):
    """Get distance between 2 points"""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def map_to_range(value, from_x, from_y, to_x, to_y):
    """map the value from one range to another"""
    return clamp(value * (to_y - to_x) / (from_y - from_x), to_x, to_y)


@lru_cache()
def load_image(path: str, alpha: bool = True, scale=1.0, color_key=None):
    img = pygame.image.load(path)
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*scale), int(h*scale)))
    if color_key:
        img.set_colorkey(color_key)
    if alpha:
        return img.convert_alpha()
    else:
        return img.convert()


class Timer:
    def __init__(self, timeout=0.0):
        self.timeout = timeout
        self.timer = time.time()
        self.paused_timer = time.time()
        self.paused = False

    def pause(self):
        self.paused = True
        self.paused_timer = time.time()

    def resume(self):
        self.paused = False
        self.timer -= time.time() - self.paused_timer

    @property
    def elapsed(self):
        if self.paused:
            return time.time() - self.timer - (time.time() - self.paused_timer)
        return time.time() - self.timer

    @property
    def tick(self):
        if self.elapsed > self.timeout:
            self.timer = time.time()  # reset timer
            return True
        else:
            return False


class SpriteSheet:
    """
    Class to load sprite-sheets
    """

    def __init__(self, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None):
        self._sheet = pygame.image.load(sheet)
        self._r = rows
        self._c = cols
        self._images = images if images else rows * cols
        self._alpha = alpha
        self._scale = scale
        self._color_key = color_key

    def __str__(self):
        return f'SpriteSheet Object <{self._sheet.__str__()}>'

    def get_images(self):
        w = self._sheet.get_width() // self._c
        h = self._sheet.get_height() // self._r
        images = [self._sheet.subsurface(pygame.Rect(i % self._c * w, i // self._c * h, w, h)) for i in range(self._r * self._c)][0:self._images]
        if self._color_key is not None:
            for i in images:
                i.set_colorkey(self._color_key)
        if self._alpha:
            for i in images:
                i.convert_alpha()
        else:
            for i in images:
                i.convert()
        return [pygame.transform.scale_by(i, self._scale) for i in images]


class LoopingSpriteSheet:
    def __init__(self, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None, timer=0.1,
                 mode: Literal['center', 'topleft'] = 'center'):
        self.timer = Timer(timeout=timer)
        self.images = SpriteSheet(sheet, rows, cols, images, alpha, scale, color_key).get_images()
        self.c = 0
        self.mode = mode

    def draw(self, surf: pygame.Surface, x, y):
        if self.timer.tick:
            self.c += 1
            self.c %= len(self.images)
        img = self.images[self.c]
        if self.mode == 'center':
            surf.blit(img, img.get_rect(center=(x, y)))
        else:
            surf.blit(img, (x, y))
