from ... import _hub


pygame = _hub.pygame
Tilesets = _hub.tmx.data.Tilesets


class IsometricMapCursor(object):
    # I haven't updated this for the new map system yet... I will do that ASAP, even though the QuarterCursor is
    # the one that will be useful for Niobepolis.
    def __init__(self, x, y, image, frame=0, visible=True):
        self.x = x
        self.y = y
        self.image = image
        self.frame = frame
        self.visible = visible

    def render(self, dest: pygame.Rect):
        if self.visible:
            self.image.render(dest, self.frame)

    def set_position(self, scene, x, y, must_be_visible=True):
        if scene.on_the_map(x, y) and (scene.get_visible(x, y) or not must_be_visible):
            self.x, self.y = x, y

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.set_position(view.isometric_map, *view._mouse_tile)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_KP8:
                self.set_position(view.isometric_map, self.x - 1, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP9:
                self.set_position(view.isometric_map, self.x, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP6:
                self.set_position(view.isometric_map, self.x + 1, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP3:
                self.set_position(view.isometric_map, self.x + 1, self.y)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP2:
                self.set_position(view.isometric_map, self.x + 1, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP1:
                self.set_position(view.isometric_map, self.x, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP4:
                self.set_position(view.isometric_map, self.x - 1, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP7:
                self.set_position(view.isometric_map, self.x - 1, self.y)
                view.focus(self.x, self.y)


class IsometricMapQuarterCursor(object):
    # A cursor that only takes up one quarter of a tile.
    def __init__(self, x, y, surf, layer, visible=True):
        self._doublex = int(x*2)
        self._doubley = int(y*2)
        self.surf = surf
        self.layer_name = layer.name
        self.visible = visible

    def render(self, view):
        if self.visible:
            sx, sy = view.screen_coords(*self.get_pos())
            mylayer = view.isometric_map.get_layer_by_name(self.layer_name)
            mydest = self.surf.get_rect(midbottom=(sx+mylayer.offsetx, sy+mylayer.offsety-2))
            view.screen.blit(self.surf, mydest)

    def set_position(self, view, x, y):
        self._doublex = int(x*2)
        self._doubley = int(y*2)

    @property
    def x(self):
        return self._doublex//2

    @property
    def y(self):
        return self._doubley//2

    def get_pos(self):
        return float(self._doublex-1)/2, float(self._doubley-1)/2

    def focus(self, view):
        view.focus(float(self._doublex - 1) / 2.0, float(self._doubley - 1) / 2.0)

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = _hub.core.proj_to_vscreen(pygame.mouse.get_pos())
            self.set_position(view, view.map_x(mouse_x, mouse_y, return_int=False),
                              view.map_y(mouse_x, mouse_y, return_int=False))
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_KP8:
                self._doublex -= 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP9:
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP6:
                self._doublex += 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP3:
                self._doublex += 1
                self.focus(view)
            elif ev.key == pygame.K_KP2:
                self._doublex += 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP1:
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP4:
                self._doublex -= 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP7:
                self._doublex -= 1
                self.focus(view)
