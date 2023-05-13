from .. import tmx
from ...compo import vscreen as core
from ... import _hub


Tilesets = tmx.data.Tilesets


class IsometricMapCursor:
    """
    I haven't updated this for the new map system yet... I will do that ASAP, even though the QuarterCursor is
    the one that will be useful for Niobepolis.
    """

    def __init__(self, x, y, image, frame=0, visible=True):
        self.x = x
        self.y = y
        self.image = image
        self.frame = frame
        self.visible = visible
        self.pyg = _hub.pygame

    def render(self, dest):  # dest: pygame.Rect
        if self.visible:
            self.image.render(dest, self.frame)

    def set_position(self, scene, x, y, must_be_visible=True):
        if scene.on_the_map(x, y) and (scene.get_visible(x, y) or not must_be_visible):
            self.x, self.y = x, y

    # def update(self, view, ev):
    #     if ev.type == self.pyg.MOUSEMOTION:
    #         self.set_position(view.isometric_map, *view._mouse_tile)
    #     elif ev.type == self.pyg.KEYDOWN:
    #         if ev.key == self.pyg.K_KP8:
    #             self.set_position(view.isometric_map, self.x - 1, self.y - 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP9:
    #             self.set_position(view.isometric_map, self.x, self.y - 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP6:
    #             self.set_position(view.isometric_map, self.x + 1, self.y - 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP3:
    #             self.set_position(view.isometric_map, self.x + 1, self.y)
    #             view.focus(self.x, self.y)
    #         elif ev.key == pygame.K_KP2:
    #             self.set_position(view.isometric_map, self.x + 1, self.y + 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP1:
    #             self.set_position(view.isometric_map, self.x, self.y + 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP4:
    #             self.set_position(view.isometric_map, self.x - 1, self.y + 1)
    #             view.focus(self.x, self.y)
    #         elif ev.key == self.pyg.K_KP7:
    #             self.set_position(view.isometric_map, self.x - 1, self.y)
    #             view.focus(self.x, self.y)


class IsometricMapQuarterCursor:
    # A cursor that only takes up one quarter of a tile.
    def __init__(self, x, y, surf, layer, visible=True):
        self._doublex = int(x * 2)
        self._doubley = int(y * 2)
        self.surf = surf
        self.layer_name = layer.name
        self.visible = visible
        self.pyg = _hub.pygame

    def render(self, dest):  # dest: pygame.Rect
        if self.visible:
            # print(type(dest))  # mapviewer
            dest.screen.blit(self.surf, (self.x, self.y))

    def set_position(self, view, x, y):
        self._doublex = int(x * 2)
        self._doubley = int(y * 2)

    @property
    def x(self):
        return self._doublex // 2

    @property
    def y(self):
        return self._doubley // 2

    def get_pos(self):
        return float(self._doublex) / 2.0, float(self._doubley) / 2.0

    def focus(self, view):
        view.focus(*self.get_pos())

    def update(self, view, ev):
        if ev.type == self.pyg.MOUSEMOTION:
            mouse_x, mouse_y = core.proj_to_vscreen(self.pyg.mouse.get_pos())
            self.set_position(view, view.map_x(mouse_x, mouse_y, return_int=False),
                              view.map_y(mouse_x, mouse_y, return_int=False))
        elif ev.type == self.pyg.KEYDOWN:
            if ev.key == self.pyg.K_KP8:
                self._doublex -= 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP9:
                self._doubley -= 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP6:
                self._doublex += 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP3:
                self._doublex += 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP2:
                self._doublex += 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP1:
                self._doubley += 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP4:
                self._doublex -= 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == self.pyg.K_KP7:
                self._doublex -= 1
                self.focus(view)
