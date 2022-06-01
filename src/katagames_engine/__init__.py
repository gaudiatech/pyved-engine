"""
+-----------------------------------------------------+
| KENGI [K]atagames [ENGI]ne                          |
| Motto ~ Never slow down the innovation              |
|                                                     |
| Main author: wkta-tom (github.com/wkta)             |
|                                                     |
| an open-source project funded by GAUDIA TECH INC.   |
| https://github.com/gaudiatech/kengi                 |
+-----------------------------------------------------+

 * defines a subset of the pygame library (chosen functions & objects)
  and creates a wrapper around it

 * allows for a swift implementation of two essential design patterns:
   Mediator and Model-View-Contoller

 * provides easy access to data structures useful in game development:
   stacks, matrices, trees, graphs, finite state machines, cellular automata

 * provides algorithms that may be tricky to code but are super-useful:
   A-star, Minimax, a FOV algorithm for a 2D grid based world,

 * is extensible: kengi is capable of receiving custom events and custom
  extensions, for example a custom GUI manager, an isometric engine, or
  antything similar, without requiring any architectural change

 * can run along with the KataSDK but can also be detached, to run independently

 * does not know ANYTHING about whether your code runs in a web browser or not,
  although the engine can be hacked to allow such a possibility

 * incentivizes you, the creator, to write clean readable easy-to-refactor &
  easy-to-reuse code!
"""

from . import _hub as hub
from . import pal
from .Injector import Injector
from ._BaseGameState import BaseGameState
from .__version__ import ENGI_VERSION
from .foundation import defs
from .foundation import shared  # must keep this line /!\ see web vm
from .ifaces.pygame import PygameIface
from .modes import GameModeMger, BaseGameMode
from .util import underscore_format, camel_case_format
from . import struct
from . import event


ver = ENGI_VERSION
one_plus_init = False
_active_state = False
_gameticker = None
_multistate_flag = False
_stack_based_ctrl = None


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def _show_ver_infos():
    print(f'KENGI - ver {ENGI_VERSION}, built on top of ')


def is_ready():
    global one_plus_init
    return one_plus_init


def bootstrap_e(info=None):
    """
    ensure the engine is ready to be used

    :param info:
    :return:
    """
    global pygame, one_plus_init, _gameticker
    if one_plus_init:
        return

    del pygame

    def _ensure_pygame(xinfo):
        # replace iface by genuine pygame lib, use this lib from now on
        if isinstance(xinfo, str):
            hub.kengi_inj.register('pygame', xinfo)
        else:
            hub.kengi_inj.set('pygame', xinfo)  # set the module directly, instead of using lazy load

    one_plus_init = True
    _show_ver_infos()
    if info is None:
        info = 'pygame'
    _ensure_pygame(info)

    event.create_manager()
    _gameticker = event.GameTicker()

    # dry import
    return get_injector()['pygame']


def init(gfc_mode='hd', caption=None, maxfps=60, screen_dim=None):
    global _active_state
    bootstrap_e()
    _active_state = True
    get_injector()['core'].init_e2(gfc_mode, caption, screen_dim)
    _gameticker.maxfps = maxfps


def get_surface():
    global _active_state
    if not is_ready():
        raise Exception('calling kengi.get_surface() while the engine isnt ready! (no previous bootstrap op.)')
    if not _active_state:
        raise Exception('kengi.init has not been called yet')
    return get_injector()['core'].get_screen()


def declare_states(gsdefinition, assoc_gscode_cls, mod_glvars=None):
    global _multistate_flag, state_stack, _stack_based_ctrl, _loaded_states
    _multistate_flag = True

    # verif
    # for ke in assoc_code_gs_cls.keys():
    #     if ke in _loaded_states.keys():
    #         print('[Warning] gamestate code {} was already taken. Overriding state(risky)...'.format(ke))
    #         del _loaded_states[ke]
    #
    # for ke, cls in assoc_code_gs_cls.items():
    #     print(cls)
    #     _loaded_states[ke] = cls(ke)
    x = gsdefinition
    y = mod_glvars

    state_stack = struct.Stack()
    _stack_based_ctrl = event.StackBasedGameCtrl(
        _gameticker, x, y, assoc_gscode_cls
    )


def get_game_ctrl():
    global _multistate_flag, _stack_based_ctrl, _gameticker
    if _multistate_flag:
        return _stack_based_ctrl
    else:
        return _gameticker


def get_manager():  # saves some time
    return event.EventManager.instance()


def flip():
    return get_injector()['core'].display_update()


def quit():  # we keep the "quit" name bc of pygame
    global _active_state

    if _active_state:
        event.EventManager.instance().hard_reset()

        event.CogObj.reset_class_state()

        get_injector()['core'].init2_done = False

        pyg = get_injector()['pygame']
        pyg.mixer.quit()
        pyg.quit()

        _active_state = False


def get_injector():
    return hub.kengi_inj


def plugin_bind(plugin_name, pypath):
    hub.kengi_inj.register(plugin_name, pypath)


def bulk_plugin_bind(darg: dict):
    """
    :param darg: association extension(plug-in) name to a pypath
    :return:
    """
    for pname, ppath in darg.items():
        plugin_bind(ppath, ppath)


# ----------------------------
# Stuff related to lazy import
# ----------------------------
pygame = PygameIface()


def __getattr__(attr_name):
    if not is_ready():
        raise AttributeError(f"kengi cannot lazy load, it hasnt bootstrap yet! (user request: {attr_name})")
    else:
        return getattr(hub, attr_name)
