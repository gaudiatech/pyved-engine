import json

from . import rpgmenu
from ... import _hub
from ... import pal
from ...core.events import EvListener, EngineEvTypes


frects = _hub.polarbear.frects
pygame = _hub.pygame


class Offer:
    """
    An Offer is a single line spoken by the NPC, "effect" is
    a callable with no parameters.
    "replies" is a list of replies.
    """
    def __init__(self, msg, effect=None, replies=()):
        self.msg = msg
        self.effect = effect
        self.replies = list(replies)

    def __str__(self):
        return self.msg

    @classmethod
    def from_json(cls, jdict):
        # We spoke about not needing a json loader yet. But, in terms of hardcoding
        # a conversation, it was just as easy to write this as to hand-code a dialogue tree.
        msg = jdict.get("msg", "Hello there!")
        effect = None
        replies = list()
        for rdict in jdict.get("replies", ()):
            replies.append(Reply.from_json(rdict))
        return cls(msg, effect, replies)

    @classmethod
    def load_jsondata(cls, jsondata):
        return cls.from_json(json.loads(jsondata))


class Reply:
    """
    A Reply is a single line spoken by the PC, leading to a new offer
    """
    def __init__(self, msg, destination=None):
        self.msg = msg
        self.destination = destination

    def __str__(self):
        return self.msg

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.msg, self.destination)

    @classmethod
    def from_json(cls, jdict):
        msg = jdict.get("msg", "And you too!")
        destination = jdict.get("destination")
        if destination:
            destination = Offer.from_json(destination)
        return cls(msg, destination)


class ConversationView(EvListener):
    """
    The View is used by the conversation when conversing.
    It has a "text" property and "render", "get_menu" methods.
    """
    TEXT_AREA = frects.Frect(-75, -100, 300, 100)
    MENU_AREA = frects.Frect(-75, 30, 300, 80)
    PORTRAIT_AREA = frects.Frect(-240, -110, 150, 225)
    CONV_BG_COL = pal.niobe['darkgreen']
    MENU_BORDER_COL = pal.punk['gray']
    DEBUG = True

    def __init__(self, root_offer, chosen_font, ft_size, portrait_fn=None, pre_render=None, li_alt_font_obj=None):
        # --------------------
        #  constructor
        # --------------------
        super().__init__()

        # n.b: need to use EmbeddedCfont, or no?
        if li_alt_font_obj:  # defaults to capello ft
            self._capfont = li_alt_font_obj
            # self.capfont = [
            #     gfx.JsonBasedCfont(capfont_path_prfix + '-b'),  # blue-ish
            #     gfx.JsonBasedCfont(capfont_path_prfix+'-a'),  # orange
            # ]
        else:
            self._capfont = None

        # - slight optim:
        self.text_rect = None
        self.menu_rect = None
        self.portrait_rect = None

        # can be used to make things faster for webctx
        self._primitive_style = False

        self.text = ''
        self.root_offer = root_offer
        self.pre_render = pre_render
        self._pg_font = pygame.font.Font(chosen_font, ft_size)
        if portrait_fn:
            self.portrait = pygame.image.load(portrait_fn).convert_alpha()
        else:
            self.portrait = None
        self.curr_offer = root_offer

        self.existing_menu = None

        if self._capfont:
            self.activefont = self._capfont[0]
            self.alternative_menu_flag = True
        else:
            self.activefont = self._pg_font
            self.alternative_menu_flag = False

    def refresh(self):
        # get the repr zero ready
        self.update_dialog_repr()

    def on_paint(self, ev):
        if self.primitive_style:
            self._primitiv_render(ev.screen)
        else:
            self._reg_render(ev.screen)

    def on_conv_step(self, ev):  # iterate over the conversation
        print('CONV step RECV in dialogue')
        self.curr_offer = ev.value
        self.update_dialog_repr()

    def on_mousemotion(self, ev):
        if self.existing_menu:
            self.existing_menu.proc_event(ev, None)

    def on_mousedown(self, ev):
        if self.existing_menu:
            self.existing_menu.proc_event(ev, None)

    def on_mouseup(self, ev):
        # /!\ its the mouse_up that allows to switch the rpgmenu state
        if self.existing_menu:
            self.existing_menu.proc_event(ev, None)

    def _primitiv_render(self, refscreen):
        pygame.draw.rect(refscreen, self.CONV_BG_COL, self.glob_rect)  # fond de fenetre
        pygame.draw.rect(refscreen, self.CONV_BG_COL, self.text_rect)

        #if not self.capfont:
            # old fashion

        _hub.polarbear.draw_text(
            self.activefont, self.text, self.text_rect, dest_surface=refscreen
        )
        # refscreen.blit(newsurf, (self.text_rect[0], self.text_rect[1]))

        #else:  # we've overriden the basic behavior
            # signatur is:
            #  text_to_surf(self, w, refsurf, start_pos, spacing=0, bgcolor=None)
        #    self.capfont[0].text_to_surf(self.text, refscreen, (self.text_rect[0], self.text_rect[1]))

        if self.portrait:
            refscreen.blit(self.portrait, self.portrait_rect)
        pygame.draw.rect(refscreen, self.CONV_BG_COL, self.menu_rect)

        if self.existing_menu:  # draw what the player can SAY
            if self.alternative_menu_flag:  # we have overriden the default behavior, when using a special kengi font
                self.existing_menu.alt_render(refscreen, self._capfont[0], self._capfont[1])

            else:  # the old fashion
                self.existing_menu.render(refscreen)

        # pourtour menu
        pygame.draw.rect(refscreen, self.MENU_BORDER_COL, (self.taquet_portrait, 148, self.dim_menux, 88), 2)

    def _reg_render(self, refscreen):
        if self.pre_render:
            self.pre_render()
        text_rect = self.TEXT_AREA.get_rect()
        dborder = _hub.polarbear.default_border
        dborder.render(text_rect)
        _hub.polarbear.draw_text(self.activefont, self.text, text_rect)
        dborder.render(self.MENU_AREA.get_rect())
        if self.existing_menu:
            self.existing_menu.render(refscreen)
        if self.portrait:
            refscreen.blit(self.portrait, self.PORTRAIT_AREA.get_rect())

    @property
    def primitive_style(self):
        return self._primitive_style

    @primitive_style.setter
    def primitive_style(self, use_new_layout: bool):
        self._primitive_style = use_new_layout

        if use_new_layout:
            print('ConversationView -> use_new_layout!')
            # modify locations as we know that (Primitive style => upscaling is set to x3)
            x = 48
            w = 192
            self.TEXT_AREA = frects.Frect(-x, -66, w, 80)
            self.MENU_AREA = frects.Frect(-x, 33, w, 80)
            self.PORTRAIT_AREA = frects.Frect(-x-100, -66, 90, 128)

            # optim:
            self.dim_menux = w+100
            self.text_rect = self.TEXT_AREA.get_rect()
            self.menu_rect = self.MENU_AREA.get_rect()
            self.portrait_rect = self.PORTRAIT_AREA.get_rect()
            self.taquet_portrait = self.portrait_rect[0]
            self.glob_rect = pygame.Rect(self.portrait_rect[0], 53, self.dim_menux, 182)

    def update_dialog_repr(self):
        if self.curr_offer:
            self.text = self.curr_offer.msg
            # create a new Menu inst.
            self.existing_menu = rpgmenu.Menu(
                self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                border=None, predraw=None, font=self.activefont
            )
            # predraw: self.render
            mymenu = self.existing_menu
            for i in self.curr_offer.replies:
                i.apply_to_menu(mymenu)
            if self.text and not mymenu.items:
                mymenu.add_item("[Continue]", None)
            else:
                mymenu.sort()
            nextfx = self.curr_offer.effect
            if nextfx:
                nextfx()
        else:
            # auto-close everything
            self.pev(EngineEvTypes.ConvFinish)
