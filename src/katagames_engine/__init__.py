"""
Author: github.com/wkta
Principles: The ultimate engine
-------------------------------
 * is a wrapper around pygame functions & objects

 * can run within the KataSDK but can also be detached and runs independently

 * does not know ANYTHING about whether it runs in web ctx or not.
 The engine can be "hacked" but this barely changes the engine's design

 * is extensible: engine needs to be able to receive extensions like a GUI manager,
 an isometric engine, etc. without any architecture change.
 To achieve this we will use the same hacking method as previously,
 basically this is like using an Injector (relates to-> Dependency Injection pattern)
 that is:
 if an extension module is called it will be searched/fetched via the Injector.
 This searching is done via __getattr__(name) and the _available_sub_modules dict. structure

"""
from . import _hub
from .Injector import Injector
from ._BaseGameState import BaseGameState
from .__version__ import ENGI_VERSION
from ._util import underscore_format, camel_case_format
from .foundation import defs
from .foundation import shared  # must keep this line /!\ see web vm

from .pygame_iface import PygameIface
from . import palettes

ver = ENGI_VERSION
pygame = PygameIface()
one_plus_init = False
_active_state = False


def _show_ver_infos():
    print(f'KENGI - ver {ENGI_VERSION}, built on top of ')


def bootstrap_e(info=None):
    """
    ensure the engine is ready to be used

    :param info:
    :return:
    """
    global pygame, one_plus_init
    if one_plus_init:
        return

    del pygame

    def _ensure_pygame(xinfo):
        # replace iface by genuine pygame lib, use this lib from now on
        if isinstance(xinfo, str):
            _hub.kengi_inj.register('pygame', xinfo)
        else:
            _hub.kengi_inj.set('pygame', xinfo)  # set the module directly, instead of using lazy load

    one_plus_init = True
    _show_ver_infos()
    if info is None:
        _ensure_pygame('pygame')
    else:
        _ensure_pygame(info)
    # dry import
    t = get_injector()['pygame']


def init(gfc_mode='hd', caption=None, maxfps=60, screen_dim=None):
    global _active_state
    bootstrap_e()
    _active_state = True
    __getattr__('legacy').legacyinit(gfc_mode, caption, maxfps, screen_dim)


def get_surface():
    return __getattr__('core').get_screen()


def flip():
    __getattr__('core').display_update()


def quit():
    global _active_state
    if _active_state:
        __getattr__('event').EventManager.instance().hard_reset()
        __getattr__('legacy').old_cleanup()
        _active_state = False


def get_injector():
    return _hub.kengi_inj


def plugin_bind(plugin_name, pypath):
    _hub.kengi_inj.register(plugin_name, pypath)


def bulk_plugin_bind(darg: dict):
    """
    :param darg: association extension(plug-in) name to a pypath
    :return:
    """
    for pname, ppath in darg.items():
        plugin_bind(ppath, ppath)


def __getattr__(targ_sm_name):
    global one_plus_init
    if one_plus_init:
        return getattr(_hub, targ_sm_name)
    else:
        raise AttributeError(f"kengi cannot load {targ_sm_name}, the engine is not init yet!")
