from .BasePygproxy import BasePygprox


class GenuinePygproxy(BasePygprox):
    """
    based off the genuine lib
    """

    def provide_pygame(self):
        import pygame as _pygame
        return _pygame

    def provide_gfxdraw(self):
        import pygame.gfxdraw as _gfxdraw
        return _gfxdraw
