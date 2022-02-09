from .BasePygproxy import BasePygprox


class EmuPygproxy(BasePygprox):

    def provide_pygame(self):
        from .. import pygame_emu as pyg
        return pyg

    def provide_gfxdraw(self):
        from ..pygame_emu import gfxdraw as gfxd
        return gfxd
