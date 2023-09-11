import pygame
# from ..core.renderable import Renderable
# from ..core.colours import WHITE
# from ..utils.utils_draw import blit_alpha
from renderable import Renderable


class Rectangle(Renderable):

    def __init__(self,
    
        # required parameters
        x, y, w, h,
        
        # optional parameters
        hAlign='left', vAlign='top',
        colour='white',
        alpha=255,
        z=1,
        xParallax=False, yParallax=False

    ):

        super().__init__(x, y, z, hAlign, vAlign, colour, alpha, xParallax, yParallax)
        
        # set additional text object parameters 
        self._w = w
        self._h = h
        self._createSurface()
    
    def _createSurface(self):
        
        self.surface = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        pygame.draw.rect(self.surface, self.colour, (0, 0, self._w, self._h))
        
        self._align()

    def draw(self, surface, xOff=0, yOff=0, scale=1):

        x = int(self.rect.x * scale + xOff)
        y = int(self.rect.y * scale + yOff)
        w = int(self.rect.w * scale)
        h = int(self.rect.h * scale)
        
        if scale != 1:
            scaled_surface = pygame.transform.scale(self.surface, (w, h))
        else:
            scaled_surface = self.surface

        if self._alpha < 255:
            blit_alpha(surface, scaled_surface, (x, y), self._alpha)
        else:
            surface.blit(scaled_surface, (x,y))

    #  dimension properties

    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = value
        self._createSurface()

    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
        self._createSurface()

