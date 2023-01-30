from .BaseGuiElement import BaseGuiElement
from ... import _hub


pygame = _hub.pygame


class WidgetContainer(BaseGuiElement):
    LTR = 1
    EXPAND = 2
    FLOW = 3

    def __init__(self, pos, size, layout_type, widget_list=None, spacing=0):
        super().__init__()
        assert isinstance(layout_type, int)

        self.set_pos(pos)
        self.set_dimensions(size)
        self.content = list()
        if widget_list is not None:
            if isinstance(widget_list, dict):
                self.dictmode = 1
                self.cpdict = dict(widget_list)
                self.content.extend(widget_list.values())
            else:
                self.dictmode = 0
                self.content.extend(widget_list)

        # adjust positions automatically!
        if layout_type == self.LTR:
            c_pos = [0, 0]
            for w in self.content:
                w.set_pos(
                    (self._abs_pos[0]+c_pos[0], self._abs_pos[1])
                )
                c_pos[0] += w.get_dimensions()[0]+spacing

        elif layout_type == self.EXPAND:
            p = self.get_pos()
            bsupx, bsupy = self._dim
            increm = bsupx // (
                        +2 - 1 + len(self.content))  # +2 because of left & right margin, -1 bc two spaces if 3 elem
            c_pos = [increm, p[1] + (self._dim[1] // 2)]
            for w in self.content:
                w.set_pos(c_pos)
                c_pos[0] += increm

        for w in self.content:
            print(w.get_pos())

        for elt in self.content:
            elt._parent = self

    def __getitem__(self, item):
        if not self.dictmode:
            raise RuntimeError
        return self.cpdict[item]

    def get_relative_rect(self):
        pass

    def set_relative_pos(self, position):
        pass

    def draw(self):
        if self._debug:
            pygame.draw.rect(self._scrref, 'red', self.get_abs_rect(), 1)

        for elt in self.content:
            elt.draw()  # refscr.blit(b.image, b.position)

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def proc_event(self, event) -> bool:
        pass

    def on_unfocus(self):
        pass

    def set_image(self, new_image):
        pass

    def set_active(self, activate_mode: bool):
        pass
