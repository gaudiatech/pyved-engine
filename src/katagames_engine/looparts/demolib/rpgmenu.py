import collections
import glob
import random

from ... import _hub
from ...compo import vscreen as core
from ...core import events


Emitter = events.Emitter
EngineEvTypes = events.EngineEvTypes
pygame = _hub.pygame  # alias to keep on using pygame, easily
Frect = _hub.polarbear.frects.Frect
ANCHOR_CENTER = _hub.polarbear.frects.ANCHOR_CENTER
ANCHOR_UPPERLEFT = _hub.polarbear.frects.ANCHOR_UPPERLEFT
default_border = _hub.polarbear.default_border
render_text = _hub.polarbear.render_text
draw_text = _hub.polarbear.draw_text
wait_event = _hub.polarbear.wait_event
TIMEREVENT = _hub.polarbear.TIMEREVENT
INFO_GREEN = _hub.polarbear.INFO_GREEN
DEFAULT_FONT_SIZE = 11
MENU_ITEM_COLOR = pygame.Color(150, 145, 130)
MENU_SELECT_COLOR = pygame.Color(128, 250, 230)

ReceiverObj = events.EvListener


class MenuItem(object):
    def __init__(self, msg, value, desc, menu):
        self.value = value
        self.desc = desc
        self._font = menu.font
        self.width = menu.w
        self.justify = -1
        self.menuitem = menu.menuitem
        self.menuselect = menu.menuselect
        self.item_image = None
        self.select_image = None
        self.height = 0
        self._msg = msg

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, v):
        self._font = v
        self._set_msg(self._msg)  # force refresh

    def _get_msg(self):
        return self._msg

    def _set_msg(self, msg):
        self._msg = msg
        # - remove the pre-computation so the webctx accepts this as well
        #self.item_image = render_text(self._font, self._msg, self.width, justify=self.justify, color=self.menuitem)
        #self.select_image = render_text(self._font, self._msg, self.width, justify=self.justify, color=self.menuselect)
        tmp = render_text(self._font, self._msg, self.width, justify=self.justify, color=self.menuselect)
        self.height = tmp.get_size()[1]

        # before tinkenig web ctx:
        # self.select_image.get_height()

    msg = property(_get_msg, _set_msg)

    SORT_LAYER = 0

    def sort_order(self):
        return self.SORT_LAYER, self._msg

    def __lt__(self, other):
        """ Comparison of menu items done by sort order, as defined above """
        return self.sort_order() < other.sort_order()

    def __str__(self):
        return self._msg

    def render(self, screen, dest, selected=False):
        # signature draw_text(font, text, rect, color=TEXT_COLOR, justify=-1, antialias=True, dest_surface=None):
        #if selected:
        draw_text(self._font, self._msg, pygame.Rect(dest[0], dest[1], self.width, 256), justify=self.justify, dest_surface=screen)
        #else:
        #    draw_text(self._font, self._msg, (dest[0], dest[1], self.width, 256), justify=self.justify, color=self.menuitem)

        # - before tinkering for the web ctx compat...
        # if selected:
        #     screen.blit(self.select_image, dest)
        # else:
        #     screen.blit(self.item_image, dest)


# The DescBox is the default MenuDesc. It takes a string stored in the menu
# item and displays it. However, it is not the only menu description possible!
# Any object with a render_desc(menu_item) method will work.
# Also note that the desc associated with each menu item doesn't need to be
# a string- it all depends on the needs of the descobj you're using.

class DescBox(Frect):
    # The DescBox inherits from Frect, since that's basically what it is.
    def __init__(self, menu, dx, dy, w=300, h=100, anchor=ANCHOR_CENTER, border=default_border, justify=-1, font=None,
                 color=None, **kwargs):
        self.menu = menu
        self.border = border
        self.justify = justify
        if not anchor:
            anchor = menu.anchor
        self.font = font or pygame.font.Font("assets/DejaVuSansCondensed-Bold.ttf", DEFAULT_FONT_SIZE)
        self.color = color or INFO_GREEN
        super(DescBox, self).__init__(dx, dy, w, h, anchor, **kwargs)

    def __call__(self, menu_item):
        mydest = self.get_rect()
        if self.border:
            self.border.render(mydest)
        if menu_item and menu_item.desc:
            img = render_text(self.font, menu_item.desc, self.w, justify=self.justify, color=self.color)
            screen.blit(img, mydest)


class Menu(Emitter, Frect):
    """
    N.B (tom) it would be much better to inherit from CogObj
    + have a Frect attribute
    """
    # TODO refactor

    def __init__(self, dx, dy, w=300, h=100, anchor=ANCHOR_CENTER, menuitem=MENU_ITEM_COLOR,
                 menuselect=MENU_SELECT_COLOR, border=default_border, predraw=None, font=None, padding=0,
                 item_class=MenuItem):
        # usin multiple inheritance
        Emitter.__init__(self)
        Frect.__init__(self, dx, dy, w, h, anchor)

        self.menuitem = menuitem
        self.menuselect = menuselect
        self.border = border
        self.font = font or pygame.font.Font("assets/DejaVuSansCondensed-Bold.ttf", DEFAULT_FONT_SIZE)
        self.more_image = self.font.render("+", True, menuselect)
        self.padding = padding
        self.item_class = item_class

        self.items = []
        self.top_item = 0
        self.selected_item = 0
        self.can_cancel = True
        self.descobj = None
        self.quick_keys = {}

        self._item_rects = collections.OrderedDict()
        self._the_highest_top = 0

        # predraw is a function that
        # redraws/clears the screen before the menu is rendered.
        self.predraw = predraw

        # -> to the model
        self.no_choice_made = True
        self.choice = False

    def add_item(self, msg, value, desc=None):
        item = self.item_class(msg, value, desc, self)
        self.items.append(item)

    def add_descbox(self, x, y, w=30, h=10, justify=-1, font=None, **kwargs):
        self.descobj = DescBox(self, x, y, w, h, border=self.border, justify=justify, font=font or self.font, **kwargs)

    def arrange(self):
        # Set the position of all on-screen menu items.
        mydest = self.get_rect()
        item_num = self.top_item
        self._item_rects.clear()
        y = mydest.top
        while y < mydest.bottom:
            if item_num < len(self.items):
                itemdest = pygame.Rect(mydest.x, y, self.w, self.items[item_num].height)
                # Only add this item to the menu if it fits inside the menu or is the first menu item.
                if itemdest.bottom <= mydest.bottom or not self._item_rects:
                    self._item_rects[item_num] = itemdest
                y += self.items[item_num].height + self.padding
            else:
                break
            item_num += 1

        # While we're here, might as well calculate the highest top.
        self._the_highest_top = len(self.items) - 1
        item_num = self._the_highest_top
        y = mydest.bottom
        while y >= mydest.top and item_num >= 0:
            y -= self.items[item_num].height
            if y >= mydest.top:
                self._the_highest_top = item_num
            item_num -= 1
            y -= self.padding

    def alt_render(self, scr, capft, select_capft, do_extras=True):
        mydest = self.get_rect()
        if do_extras:
            if self.predraw:
                self.predraw(scr)
            if self.border:
                self.border.render(mydest)

        scr.set_clip(mydest)
        self.arrange()
        for item_num, area in list(self._item_rects.items()):
            # THIS IS THE LINE THAT's rly different
            # signatur is:
            #  text_to_surf(self, w, refsurf, start_pos, spacing=0, bgcolor=None)
            # debug - print(type(self.items[item_num]))

            #TODO if selected then use the select_capft to render txt !
            if item_num == self.selected_item:
                pfont = select_capft
            else:
                pfont = capft
            self.items[item_num].font = pfont
            self.items[item_num].render(scr, area, False)
            # pfont.text_to_surf(self.items[item_num].msg, scr, (area[0], area[1]))

        scr.set_clip(None)
        # tom: dunno what its for?
        # if self.descobj:
        #     self.descobj(self.get_current_item())

    def render(self, scr, do_extras=True):
        mydest = self.get_rect()
        if do_extras:
            if self.predraw:
                self.predraw(scr)
            if self.border:
                self.border.render(mydest)

        scr.set_clip(mydest)
        self.arrange()
        for item_num, area in list(self._item_rects.items()):
            self.items[item_num].render(scr, area, (item_num == self.selected_item) and do_extras)
        scr.set_clip(None)
        if self.descobj:
            self.descobj(self.get_current_item())

    def get_mouseover_item(self, pos):
        # Return the menu item under this mouse position.
        # self.arrange must have been called previously!
        for item_num, area in list(self._item_rects.items()):
            if area.collidepoint(pos):
                return item_num

    def query(self):
        # TODO refactor this, so it doesnt hook the game loop anymore

        # A return of False means selection was cancelled.
        # pygame.event.clear()
        if not self.items:
            return False
        elif self.selected_item >= len(self.items):
            self.selected_item = 0
        self.no_choice_made = True
        self.choice = False

        # Do an initial arrangement of the menu.
        self.arrange()

    def proc_event(self, kengi_ev, source):
        """
        since may 2022,
        the new way to return "choice" values, is via posting an event
        """
        # while no_choice_made:
        #     pc_input = wait_event()

        # if pc_input.type == TIMEREVENT:
        #     # Redraw the menu on each timer event.
        #     self.render()
        #     kengi.flip()

        if kengi_ev.type == EngineEvTypes.Keydown:
            # A key was pressed, oh happy day! See what key it was and act
            # accordingly.
            if kengi_ev.key == pygame.K_UP:
                self.selected_item -= 1
                if self.selected_item < 0:
                    self.selected_item = len(self.items) - 1
                if self.selected_item not in self._item_rects:
                    self.top_item = min(self.selected_item, self._the_highest_top)
            elif kengi_ev.key == pygame.K_DOWN:
                self.selected_item += 1
                if self.selected_item >= len(self.items):
                    self.selected_item = 0
                if self.selected_item not in self._item_rects:
                    self.top_item = min(self.selected_item, self._the_highest_top)
            elif kengi_ev.key == pygame.K_SPACE or kengi_ev.key == pygame.K_RETURN:
                self.pev(EngineEvTypes.ConvStart, value=self.items[self.selected_item].value)
                self.no_choice_made = False
            elif (kengi_ev.key == pygame.K_ESCAPE or kengi_ev.key == pygame.K_BACKSPACE) and self.can_cancel:
                self.no_choice_made = False
            elif 0 <= kengi_ev.key < 256 and chr(kengi_ev.key) in self.quick_keys:
                self.pev(EngineEvTypes.ConvStep, value=self.quick_keys[chr(kengi_ev.key)])
                self.no_choice_made = False
            elif kengi_ev.key > 255 and kengi_ev.key in self.quick_keys:
                self.pev(EngineEvTypes.ConvStep, value=self.quick_keys[kengi_ev.key])
                self.no_choice_made = False

        elif kengi_ev.type == EngineEvTypes.Mousedown:
            if kengi_ev.button == 1:
                mouse_pos = core.proj_to_vscreen(pygame.mouse.get_pos())
                moi = self.get_mouseover_item(mouse_pos)
                if moi is not None:
                    self.set_item_by_position(moi)
            elif kengi_ev.button == 4:
                self.top_item = max(self.top_item - 1, 0)
            elif kengi_ev.button == 5:
                self.top_item = min(self.top_item + 1, self._the_highest_top)

        elif kengi_ev.type == EngineEvTypes.Mouseup:
            mouse_pos = core.proj_to_vscreen(pygame.mouse.get_pos())

            if kengi_ev.button == 1:
                moi = self.get_mouseover_item(mouse_pos)
                if moi is self.selected_item:
                    self.pev(EngineEvTypes.ConvStep, value=self.items[self.selected_item].value)
                    self.no_choice_made = False

            elif kengi_ev.button == 3 and self.can_cancel:
                self.no_choice_made = False

        elif kengi_ev.type == EngineEvTypes.Mousemotion:
            mouse_pos = core.proj_to_vscreen(pygame.mouse.get_pos())
            moi = self.get_mouseover_item(mouse_pos)
            if moi is not None:
                self.set_item_by_position(moi)

    def sort(self):
        self.items.sort()

    alpha_key_sequence = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    def add_alpha_keys(self):
        # Adds a quick key for every item currently in the menu.
        key_num = 0
        for item in self.items:
            item.msg = self.alpha_key_sequence[key_num] + ') ' + item.msg
            self.quick_keys[self.alpha_key_sequence[key_num]] = item.value
            key_num += 1
            if key_num >= len(self.alpha_key_sequence):
                break

    def add_files(self, filepat):
        file_list = glob.glob(filepat)

        for f in file_list:
            self.add_item(f, f)
        self.sort()

    def reposition(self):
        self.arrange()
        if self.selected_item < self.top_item:
            self.top_item = self.selected_item
        elif self.selected_item > max(self._item_rects.keys()):
            self.top_item = max(list(self._item_rects.keys()) + [self._the_highest_top])
        self.arrange()

    def has_value(self, v):
        for i in self.items:
            if i.value == v:
                return True

    def set_item_by_value(self, v):
        for n, i in enumerate(self.items):
            if i.value == v:
                self.selected_item = n
        self.reposition()

    def set_item_by_position(self, n):
        if n < len(self.items):
            self.selected_item = n
        self.reposition()

    def set_random_item(self):
        if self.items:
            n = random.randint(0, len(self.items) - 1)
            self.set_item_by_position(n)

    def get_current_item(self):
        if self.selected_item < len(self.items):
            return self.items[self.selected_item]

    def get_current_value(self):
        if self.selected_item < len(self.items):
            return self.items[self.selected_item].value


class PopUpMenu(Menu):
    """Creates a small menu at the current mouse position."""

    def __init__(self, w=200, h=250, predraw=None, border=default_border, **kwargs):
        mouse_pos = core.proj_to_vscreen(pygame.mouse.get_pos())
        x, y = mouse_pos
        x += 8
        y += 8
        sw, sh = core.get_screen().get_size()
        if x + w + 32 > sw:
            x += -w - 32
        if y + h + 32 > sh:
            y += -h - 32

        super().__init__(x, y, w, h, ANCHOR_UPPERLEFT, border=border, predraw=predraw, **kwargs)


class AlertMenu(Menu):
    WIDTH = 350
    HEIGHT = 250
    MENU_HEIGHT = 75

    FULL_RECT = Frect(-175, -125, 350, 250)
    TEXT_RECT = Frect(-175, -125, 350, 165)

    def __init__(self, desc):
        super().__init__(-self.WIDTH // 2, self.HEIGHT // 2 - self.MENU_HEIGHT, self.WIDTH, self.MENU_HEIGHT,
                         border=None, predraw=self.pre)
        self.desc = desc

    def pre(self):
        default_border.render(self.FULL_RECT.get_rect())
        draw_text(self.font, self.desc, self.TEXT_RECT.get_rect(), justify=0)
