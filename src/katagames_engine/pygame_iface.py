"""
Author: wkta-tom
 | thomas@gaudia-tech.com

This (very strange?) file is here only to describe/identify
a subset of pygame, contrary to appearances
creating this file is useful so Kengi becomes "connectable" to other software
components for example to KataSDK, or to KtgVM...

In other words Kengi does not use 100% of pygame capabilities
and it's better this way for many reasons I don't explain here.
"""


class PygameDrawIface:

    @staticmethod
    def circle(surface, color, pos, radius):
        pass

    @staticmethod
    def rect(surface, bidule):
        pass


class PygameMathIface:

    def Vector2(self, **args):
        pass


class PygameIface:

    draw = PygameDrawIface
    math = PygameMathIface

    KEYDOWN = -1
    KEYUP = 2
    K_LEFT = 3

    @staticmethod
    def Color(rgb):
        pass
