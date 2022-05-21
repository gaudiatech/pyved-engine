import katagames_engine as kengi

pygame = kengi.pygame  # alias to keep on using pygame, easily
screen = kengi.core.get_screen()  # new way to retrieve the surface used for display

import copy
from . import rpgmenu
from pbge import default_border, frects, draw_text
import json


class Offer(object):
    # An Offer is a single line spoken by the NPC.
    # "effect" is a callable with no parameters.
    # "replies" is a list of replies.
    def __init__(
            self, msg, effect=None, replies=()
    ):
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
    def load_json(cls, filename):
        with open(filename) as f:
            jdict = json.load(f)
        return cls.from_json(jdict)


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


class SimpleVisualizer(object):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = frects.Frect(-75, -100, 300, 100)
    MENU_AREA = frects.Frect(-75, 30, 300, 80)
    PORTRAIT_AREA = frects.Frect(-240,-110,150,225)

    def __init__(self, root_offer, pre_render=None):
        self.text = ''
        self.root_offer = root_offer
        self.pre_render = pre_render
        self.font = pygame.font.Font("assets/DejaVuSansCondensed-Bold.ttf", 13)
        self.portrait = pygame.image.load("assets/mysterious_stranger.png").convert_alpha()

    def render(self):
        if self.pre_render:
            self.pre_render()
        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(self.font, self.text, text_rect)
        default_border.render(self.MENU_AREA.get_rect())
        screen.blit(self.portrait, self.PORTRAIT_AREA.get_rect())

    def get_menu(self):
        return rpgmenu.Menu(self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h, border=None,
                            predraw=self.render)

    def converse(self):
        # coff is the "current offer"
        coff = self.root_offer
        while coff:
            self.text = coff.msg
            mymenu = self.get_menu()
            for i in coff.replies:
                i.apply_to_menu(mymenu)
            if self.text and not mymenu.items:
                mymenu.add_item("[Continue]", None)
            else:
                mymenu.sort()
            nextfx = coff.effect

            coff = mymenu.query()

            if nextfx:
                nextfx()
