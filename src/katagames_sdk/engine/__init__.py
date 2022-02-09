"""
interface to the Kata.games game Engine
 alias "kataen"

GAUDIA TECH INC.
 (c) 2018-2021

Author:
 Thomas Iwaszko
"""

from . import legacy as eng_
from .foundation import conf_eng as cgmconf, events as kevent
from .foundation import defs as _defs
from ..alpha_pyg.PygproxyBringer import PygproxyBringer as _BringerCls
from ._BaseGameState import BaseGameState

# --------------------------------------------------
# [  ! ]_FORCE_ expose objects_[ !  ]
# --------------------------------------------------
from .AnimatedSprite import AnimatedSprite
from .foundation.defs import HD_MODE, OLD_SCHOOL_MODE, SUPER_RETRO_MODE
e = AnimatedSprite or HD_MODE or OLD_SCHOOL_MODE or SUPER_RETRO_MODE

from .foundation.events import EventReceiver, EngineEvTypes, CogObject, EventManager, CgmEvent
e = e or EventReceiver or EngineEvTypes or CogObject or EventManager or CgmEvent

from .foundation.conf_eng import runs_in_web as _r_web_context

from .foundation.defs import enum_for_custom_event_types
e = e or enum_for_custom_event_types

from .foundation.gfx_updater import display_update
e = e or display_update


# 4 methods below are kept only for improved backward compat' (SDK) ----------
def runs_in_web():
    return _BringerCls.instance().web_enabled


def import_gfxdraw():
    return _BringerCls.instance().pygame_gfxdraw()


def import_pygame():
    return _BringerCls.instance().pygame()


def embody_lib(givenmodule):
    print('*** warning embody_lib is now deprecated! ***')
    print('calling this function has no effect.')

# -------------------- end improved backward compat' --------------------


# - variables privées du module
_cached_screen = None


def screen_size():
    global _cached_screen
    if _cached_screen is None:
        _cached_screen = cgmconf.screen
    return _cached_screen.get_size()


def target_upscaling(mode):
    return {
        SUPER_RETRO_MODE: 3,
        OLD_SCHOOL_MODE: 2,
        HD_MODE: 1
    }[mode]


def target_w(mode):
    if mode == SUPER_RETRO_MODE:
        return 960 // 3
    if mode == OLD_SCHOOL_MODE:
        return 960 // 2
    return 960


def target_h(mode):
    if mode == SUPER_RETRO_MODE:
        return 540 // 3
    if mode == OLD_SCHOOL_MODE:
        return 540 // 2
    return 540


# -----------------------------------
# -<>- public procedures: engine -<>-
# -----------------------------------
def init(mode=HD_MODE):
    """
    :param mode: type str, describes what gfx mode we are using
    :return: nothing
    """
    bringer = _BringerCls.instance()

    # we "push higher" the data, for an easier access from within the foundation sub-module
    cgmconf.runs_in_web = bringer.web_enabled
    cgmconf.pygame = bringer.pygame()
    cgmconf.pygame_gfxdraw = bringer.pygame_gfxdraw()

    kevent.PygameBridge = cgmconf.pygame.constants
    eng_.legacyinit(cgmconf.pygame, mode)
    kevent.gl_unique_manager = get_manager()


def get_game_ctrl():
    return eng_.retrieve_game_ctrl()


def cleanup():
    eng_.cleanup()


def get_manager():
    if cgmconf.runs_in_web:
        pygm = cgmconf.pygame
        return pygm.key.linkto_ev_manager
    else:
        return EventManager.instance()


def get_screen():
    return cgmconf.screen


# -----------------------------------
# -<>- public procedures: utils -<>-
# -----------------------------------

def proj_to_vscreen(org_screen_pos):
    return cgmconf.conv_to_vscreen(*org_screen_pos)
