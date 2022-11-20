import random
from typing import Union, Tuple

import pygame

from .interfaces.element_interface import IfaceUIElement
from ...foundation import event2 as evmodule
from ...compo import vscreen


SPATIAL_INFO = Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]
ANCHOR_CENTER, ANCHOR_RIGHT, ANCHOR_LEFT = range(34151, 34151+3)


class GenericUIElement(IfaceUIElement):
    """
    almost abstract element, all it contains is the minimal code,
    so it can be visually debugged
    """

    def __init__(self, position0: SPATIAL_INFO, dimensions0: SPATIAL_INFO, anchoring=None, debugmode=False):
        super().__init__()

        # state/sys
        self._debug_mode = debugmode
        self._is_active = True
        self._cached_scr_ref = None

        # regular attributes
        self._dim = [-1, -1]
        self.set_dimensions(dimensions0)

        self._curr_anchor = ANCHOR_LEFT  # the default one
        if anchoring:
            self.set_anchoring(anchoring)

        self._xy_coords = [0, 0]
        self.set_position(position0)

        self._hovered_rn = False

    # ----------------------------
    #  handy, even if not made explicit by the iface
    # ----------------------------
    @property
    def x(self):
        return self.get_position()[0]

    @x.setter
    def x(self, newx):
        self.set_position((newx, self.y))

    @property
    def y(self):
        return self.get_position()[1]

    @y.setter
    def y(self, newy):
        self.set_position((self.x, newy))

    # ----------
    #  reg methods implem
    # ----------
    def rebuild(self) -> None:
        pass

    def get_position(self):
        hw, hh = self._dim
        hw = int(hw / 2)
        hh = int(hh / 2)
        return self._xy_coords[0]+hw, self._xy_coords[1]+hh

    def set_position(self, position: SPATIAL_INFO):
        # args passed are absolute!
        if self._curr_anchor == ANCHOR_LEFT:
            self._xy_coords[0], self._xy_coords[1] = position

        elif self._curr_anchor == ANCHOR_CENTER:
            hw, hh = self._dim
            hw = int(hw/2)
            hh = int(hh/2)
            self._xy_coords[0] = position[0] - hw
            self._xy_coords[1] = position[1] - hh

    def set_relative_position(self, position: SPATIAL_INFO):
        # TODO
        raise Exception

    def get_dimensions(self):
        return self._dim

    def set_dimensions(self, dimensions: SPATIAL_INFO):
        self._dim[0], self._dim[1] = dimensions

    def get_relative_rect(self) -> pygame.Rect:
        pass

    def get_abs_rect(self) -> pygame.Rect:
        pass

    def update(self, time_delta: float):
        # GenericUIElement doesnt react
        pass

    def draw(self):
        if not self._cached_scr_ref:
            self._cached_scr_ref = vscreen.screen
        if self._debug_mode:
            pygame.draw.rect(
                self._cached_scr_ref,
                'red',
                (self._xy_coords[0]-1, self._xy_coords[1]-1, self._dim[0]+1, self._dim[1]+1),
                2  # line width
            )

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def proc_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            mx, my = vscreen.proj_to_vscreen(event.pos)
            if not self._hovered_rn:
                if self._xy_coords[0] < mx < self._xy_coords[0]+self._dim[0]:
                    if self._xy_coords[1] < my < self._xy_coords[1]+self._dim[1]:
                        self._hovered_rn = True
                        self.on_hover()

            if self._hovered_rn:
                hit = False
                if self._xy_coords[0] < mx < self._xy_coords[0]+self._dim[0]:
                    if self._xy_coords[1] < my < self._xy_coords[1]+self._dim[1]:
                        hit = True
                if not hit:
                    self._hovered_rn = False
                    self.on_unhover()
            return True
        else:
            return False

    def set_debug_mode(self, activate_mode: bool):
        self._debug_mode = activate_mode

    def set_image(self, new_image: Union[pygame.surface.Surface, None]):
        pass

    def set_active(self, activate_mode: bool):
        self._is_active = True

    def set_anchoring(self, anch_code):
        self._curr_anchor = anch_code

    def get_anchoring(self) -> int:
        pass

    # ---------------------------
    #  CAN be re-defined later (callbacks)
    # ---------------------------
    def on_hover(self):
        pass

    def on_unhover(self):
        pass

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass


class Button(GenericUIElement):
    pass  # TODO


class AugmentedSprite(GenericUIElement):
    """
    it's like a sprite but can be clicked/hovered/focused
    """
    def __init__(self, img, anchoring=None):
        img_dim = img.get_size()
        self._inner_sprite = pygame.sprite.Sprite()
        self._inner_sprite.image = img
        self._inner_sprite.rect = img.get_rect()

        super().__init__((0, 0), img_dim, anchoring)
        self.callback = None  # can be used whenever the element is clicked!

    # redefine
    def set_position(self, position: SPATIAL_INFO):
        super().set_position(position)
        self._inner_sprite.rect.center = position

    # def on_paint(self, ev):
    #     super().draw()
    #     ev.screen.blit(self._inner_sprite.image, self._inner_sprite.rect.topleft)
    #
    # def on_mousedown(self, ev):
    #     print('x')

    def proc_event(self, event: pygame.event.Event) -> bool:
        if self._is_active:
            super().proc_event(event)

            #if event.type == evmodule.EngineEvTypes.PAINT:
            #    self.draw()

            if event.type == pygame.MOUSEBUTTONDOWN:
                print('augmented spr knows click')
                updated_pos = vscreen.proj_to_vscreen(event.pos)

                if self._inner_sprite.rect.collidepoint(updated_pos):  # hit
                    print('HIT on augmented sprite detected...')
                    if self.callback is not None:
                        self.callback(event.button)

            return True
        else:
            return False


class WidgetContainer(GenericUIElement):
    LTR = 1
    EXPAND = 2

    def __init__(self, pos, size, widget_list, layout_type=LTR):
        super().__init__(pos, size)
        self.content = list()
        self.content.extend(widget_list)

        # adjust positions automatically!
        if layout_type == self.LTR:
            c_pos = [0, 0]
            for w in widget_list:
                w.set_position(c_pos)
                c_pos[0] += w.get_dimensions()[0]
                c_pos[1] = self._xy_coords[1]

        elif layout_type == self.EXPAND:
            bsupx, bsupy = self._dim
            increm = bsupx // (+2-1+len(self.content))  # +2 because of left & right margin, -1 bc two spaces if 3 elem
            c_pos = [increm, self._xy_coords[1] + (self._dim[1] // 2)]
            for w in widget_list:
                w.set_position(c_pos)
                c_pos[0] += increm


class _SprLikeLabel(pygame.sprite.Sprite):
    # TODO make it a UIelement

    def __init__(self, txt, txtsize, color=None):
        self._font = pygame.font.Font(None, txtsize)

        super().__init__()

        self._txt = txt

        self._color = [0, 0, 0]
        if color:
            try:
                self._color[0], self._color[1], self._color[2] = color.r, color.g, color.b
            except (ValueError, AttributeError):
                # force conversion to color
                c = pygame.color.Color(color)
                self._color[0], self._color[1], self._color[2] = c.r, c.g, c.b
        # init image & rect, as well!
        self.color = self._color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.image = self._font.render(self._txt, False, value)
        self.rect = self.image.get_rect()


class Label(GenericUIElement):

    def __init__(self, position, text, txtsize=35, color=None, anchoring=ANCHOR_LEFT, debugmode=False):
        self._used_text = text
        self._used_color = color
        self.txtsize = txtsize
        self._inner_spr = _SprLikeLabel(text, txtsize, color)
        super().__init__(position, self._inner_spr.rect.size, anchoring, debugmode)

    @property
    def text(self):
        return self._used_text

    # modifiying text => rebuild step
    @text.setter
    def text(self, newtext):
        self._used_text = newtext
        self.rebuild()

    def rebuild(self) -> None:
        """
        called if the spr has changed (or the color)
        :return:
        """
        self._inner_spr = _SprLikeLabel(self._used_text, self.txtsize, self._used_color)
        super().__init__(self.get_position(), self._inner_spr.rect.size, self._curr_anchor, self._debug_mode)

    def draw(self):
        super().draw()
        topleft_coords = self._xy_coords
        self._cached_scr_ref.blit(self._inner_spr.image, topleft_coords)

    @property
    def color(self):
        return self._inner_spr.color

    @color.setter
    def color(self, newval):
        self._used_color = newval
        self.rebuild()

    # @property
    # def text(self):
    #     return self._inner_spr.color
    #
    # @text.setter
    # def text(self, newval):
    #     self._used_color = newval
    #     self.rebuild()


if __name__ == '__main__':
    pygame.init()
    scr = pygame.display.set_mode((400, 300))
    gameover = False
    cl = pygame.time.Clock()
    central_obj = _SprLikeLabel('salut', 'steelblue')

    while not gameover:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                gameover = True
            elif ev.type == pygame.KEYDOWN:
                central_obj.color = random.choice(('antiquewhite2', 'orange', 'pink', 'yellow'))

            scr.fill('grey22')
            scr.blit(central_obj.image, central_obj.rect.topleft)
            pygame.display.update()
            cl.tick(60)

    pygame.quit()
    print('test over')
