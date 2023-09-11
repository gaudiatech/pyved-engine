

class Renderable:
    
    def __init__(self, x, y, z, h, v, c, a=255, xp=False, yp=False):
        
        self._x = x
        self._y = y
        self.z = z
        self.hAlign = h
        self.vAlign = v
        self.colour = c
        self._alpha = a
        self.xp = xp
        self.yp = yp
    
    def _align(self):

        if self.rect is None:
            return

        # adjust x position for horizontal anchor
        if self.hAlign == 'left':
            self.rect.x = self._x
        if self.hAlign == 'center':
            self.rect.centerx = self._x
        if self.hAlign == 'right':
            self.rect.right = self._x

        # adjust y position for vertical anchor
        if self.vAlign == 'top':
            self.rect.y = self._y
        if self.vAlign == 'middle':
            self.rect.centery = self._y
        if self.vAlign == 'bottom':
            self.rect.bottom = self._y
    
    def _createSurface(self):
        pass

    # alpha property

    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        self._createSurface()

    # position properties

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self.hAlign = 'left'
        self._align()

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self.vAlign = 'top'
        self._align()

    @property
    def left(self):
        return self.rect.x

    @left.setter
    def left(self, value):
        self._x = value
        self.hAlign = 'left'
        self._align()

    @property
    def center(self):
        return self.rect.centerx
    
    @center.setter
    def center(self, value):
        self._x = value
        self.hAlign = 'center'
        self._align()

    @property
    def right(self):
        return self.rect.right

    @right.setter
    def right(self, value):
        self._x = value
        self.hAlign = 'right'
        self._align()

    @property
    def top(self):
        return self.rect.y

    @top.setter
    def top(self, value):
        self._y = value
        self.vAlign = 'top'
        self._align()

    @property
    def middle(self):
        return self.rect.centery

    @middle.setter
    def middle(self, value):
        self._y = value
        self.vAlign = 'middle'
        self._align()

    @property
    def bottom(self):
        return self.rect.bottom

    @bottom.setter
    def bottom(self, value):
        self._y = value
        self.vAlign = 'bottom'
        self._align()
