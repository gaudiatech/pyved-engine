import json

from . import rpgmenu
from ... import _hub as kengi
from ... import event
from ... import pal

# - aliases
frects = kengi.polarbear.frects
kengi.polarbear.draw_text
draw_text = kengi.polarbear.draw_text
pygame = kengi.pygame

EngineEvTypes = event.EngineEvTypes
EventReceiver = event.EventReceiver


class Offer(object):
    # An Offer is a single line spoken by the NPC.
    # "effect" is a callable with no parameters.
    # "replies" is a list of replies.
    def __init__(self, msg, effect=None, replies=()):
        self.msg = msg
        self.effect = effect
        self.replies = list(replies)

    def __str__(self):
        return self.msg

    @classmethod
    def from_json(cls, jdict):
        # We spoke about not needing a json loader yet. But, in terms of hardcoding a conversation, it was just as
        # easy to write this as to hand-code a dialogue tree.
        msg = jdict.get("msg", "Hello there!")
        effect = None
        replies = list()
        for rdict in jdict.get("replies", ()):
            replies.append(Reply.from_json(rdict))
        return cls(msg, effect, replies)

    @classmethod
    def load_jsondata(cls, jsondata):
        return cls.from_json(json.loads(jsondata))


class Reply(object):
    # A Reply is a single line spoken by the PC, leading to a new offer
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


class ConversationView(EventReceiver):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = frects.Frect(-75, -100, 300, 100)
    MENU_AREA = frects.Frect(-75, 30, 300, 80)
    PORTRAIT_AREA = frects.Frect(-240, -110, 150, 225)

    BGCOL = pal.punk['nightblue'] # '#221031'

    DEBUG = True

    @property
    def primitive_style(self):
        return self._primitive_style

    @primitive_style.setter
    def primitive_style(self, v):
        self._primitive_style = v

        # modify locations as we know that (Primitive style => upscaling is set to x3)
        x = 48 #58
        w = 192
        self.refxxx = x

        self.TEXT_AREA = frects.Frect(-x, -66, w, 80)
        self.MENU_AREA = frects.Frect(-x, 33, w, 80)
        self.PORTRAIT_AREA = frects.Frect(-x-100, -66, 90, 128)

        # optim:
        self.dim_menux = w+104

        self.text_rect = self.TEXT_AREA.get_rect()
        self.menu_rect = self.MENU_AREA.get_rect()
        self.portrait_rect = self.PORTRAIT_AREA.get_rect()
        self.taquet_portrait = self.portrait_rect[0]
        self.glob_rect = pygame.Rect(self.portrait_rect[0], 53, self.dim_menux, 182)


    def _primitiv_render(self, refscreen):
        pygame.draw.rect(refscreen, self.BGCOL, self.glob_rect)  # fond de fenetre

        pygame.draw.rect(refscreen, self.BGCOL, self.text_rect)
        draw_text(self.font, self.text, self.text_rect)

        if self.portrait:
            refscreen.blit(self.portrait, self.portrait_rect)

        pygame.draw.rect(refscreen, self.BGCOL, self.menu_rect)
        if self.existing_menu:
            self.existing_menu.render(refscreen)
        # pourtour menu
        pygame.draw.rect(refscreen, pal.punk['darkpurple'], (self.taquet_portrait, 148, self.dim_menux, 88), 2)

    def __init__(self, root_offer, chosen_font, ft_size, portrait_fn=None, pre_render=None):
        super().__init__()
        # - slight optim:
        self.text_rect = None
        self.menu_rect = None
        self.portrait_rect = None

        self._primitive_style = False  # can be used to make things faster for webctx
        self.zombie = False

        self.text = ''
        self.root_offer = root_offer
        self.pre_render = pre_render
        self.font = pygame.font.Font(chosen_font, ft_size)
        if portrait_fn:
            self.portrait = pygame.image.load(portrait_fn).convert_alpha()
        else:
            self.portrait = None

        self.curr_offer = root_offer
        self.dialog_upto_date = False
        self.existing_menu = None

    # def turn_off(self):  # because the conversation view can be closed from "outside" i.e. the main program
    #     if self.DEBUG:
    #         print('Conversation view closed')
    #
    #     if self.existing_menu:
    #         self.existing_menu.turn_off()
    #     super().turn_off()

    def update_dialog(self):
        if self.zombie:
            return

        if self.curr_offer is None:
            # auto-close everything
            self.pev(EngineEvTypes.CONVENDS)
            self.turn_off()
            self.zombie = True
            return

        if self.dialog_upto_date:
            return
        self.dialog_upto_date = True
        self.text = self.curr_offer.msg

        # create a new Menu inst.
        self.existing_menu = rpgmenu.Menu(
            self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
            border=None, predraw=None, font=self.font)  # predraw: self.render

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

    def proc_event(self, ev, source):
        if self.existing_menu:
            self.existing_menu.proc_event(ev, None)  # forward event to menu if it exists

        if ev.type == EngineEvTypes.PAINT:
            self.render(ev.screen)

        elif ev.type == EngineEvTypes.LOGICUPDATE:
            self.update_dialog()

        elif ev.type == EngineEvTypes.CONVCHOICE:  # ~ iterate over the conversation...
            print('ConvChoice event received by', self.__class__.__name__)
            self.dialog_upto_date = False
            self.curr_offer = ev.value

    def _reg_render(self, refscreen):
        if self.pre_render:
            self.pre_render()
        text_rect = self.TEXT_AREA.get_rect()
        dborder = kengi.polarbear.default_border

        dborder.render(text_rect)
        draw_text(self.font, self.text, text_rect)
        dborder.render(self.MENU_AREA.get_rect())

        if self.existing_menu:
            self.existing_menu.render(refscreen)

        if self.portrait:
            refscreen.blit(self.portrait, self.PORTRAIT_AREA.get_rect())

    def render(self, scr):
        if self.primitive_style:
            self._primitiv_render(scr)
        else:
            self._reg_render(scr)
