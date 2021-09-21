"""
----------------------------------------------
a KataSDK component: the game Engine

    Alias "kataen"
----------------------------------------------

 
GAUDIA TECH INC.
 (c) 2018-2021

Authors:
 - Thomas Iwaszko
 - ...
 
LICENSE for the game Engine:
LGPL-3

"""

import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf
import katagames_sdk.capsule.engine_ground.legacy as eng_
import katagames_sdk.capsule.event as kevent
import katagames_sdk.capsule.gui as gui
import katagames_sdk.capsule.pygame_provider as pygp
from katagames_sdk.capsule.engine_ground import gfx_updater
from katagames_sdk.capsule.engine_ground.BaseGameState import BaseGameState
from katagames_sdk.capsule.engine_ground.defs import EngineEvTypes
from katagames_sdk.capsule.engine_ground.defs import enum_for_custom_event_types
from katagames_sdk.capsule.engine_ground.legacy import retrieve_game_ctrl, tag_multistate, get_manager
from katagames_sdk.capsule.event import EventReceiver, CgmEvent, CogObject
from katagames_sdk.capsule.struct.misc import enum_builder
from katagames_sdk.capsule.bioslike.KataFrameV import BIOS_BG_COL_DESC, BIOS_FG_COL_DESC
from katagames_sdk.capsule.pygame_provider import import_gfxdraw

SUPER_RETRO_MODE = 'superretro'
OLD_SCHOOL_MODE = 'oldschool'
HD_MODE = 'hd'


# -<>- this is a dirty trick -<>-
# it has been put here for ONE sole purpose -> avoid auto-delete significant import lines... -<>>-
t = [
    gui, BaseGameState, enum_builder, EventReceiver, EngineEvTypes, CgmEvent, CogObject,
    enum_for_custom_event_types, retrieve_game_ctrl, tag_multistate, get_manager,
    BIOS_BG_COL_DESC, BIOS_FG_COL_DESC, import_gfxdraw
]
print(str(t)[:1]+'katasdk '+cgmconf.VERSION+' - https://kata.games/developers]')
# end of dirty trick


_nb_init = 0


# -<>- public procedures -<>-
def cleanup():
    eng_.cleanup(import_pygame())


def get_screen():
    return cgmconf.get_screen()


def proj_to_vscreen(org_screen_pos):
    return cgmconf.conv_to_vscreen(*org_screen_pos)


def get_mouse_pos():
    return proj_to_vscreen(pygp.get_module().mouse.get_pos())


def get_game_ctrl():
    return eng_.retrieve_game_ctrl()


def runs_in_web():
    import katagames_sdk.capsule.pygame_provider as pygp
    return pygp.test_web_context()


def init(mode=''):
    """
    :param mode: type str, describes what gfx mode we are using
    :return: nothing
    """

    global _nb_init
    if _nb_init:
        raise PermissionError('ERROR: calling kataen.init(mode) 2x or more is forbidden!')
    _nb_init += 1  # lock

    pygame_pym = import_pygame()
    kevent.PygameBridge = import_pygame().constants

    cgmconf.renseigne(runs_in_web())
    if mode == '':  # DEFAULT to HD mode
        mode = HD_MODE
    upscalin_v = eng_.init(pygame_pym, mode)
    gfx_updater.config_display(pygame_pym, runs_in_web(), upscalin_v)


def import_pygame():
    return pygp.get_module()
