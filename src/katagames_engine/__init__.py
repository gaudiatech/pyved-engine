"""
Author: github.com/wkta
Principles: The ultimate engine
-------------------------------
 * is a wrapper around pygame functions & objects

 * runs best within the KataSDK but can also be detached and runs independently.
 Just rename _engine -> engine, and Voila

 * does not know ANYTHING about whether it runs in web ctx or not.
 The engine can be "hacked" so it runs a pygame emulator instead of pygame,
 but this does not change anythin' to engine's implementation per se

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
from .pygame_iface import PygameIface


ver = ENGI_VERSION
pygame = PygameIface()
init_done = False


def init(gfc_mode='hd', pygame_mod_info='pygame'):
    global pygame
    global init_done

    if not init_done:
        init_done = True
        # replace iface by genuine pygame lib, use this lib from now on
        del pygame
        if isinstance(pygame_mod_info, str):
            _hub.kengi_inj.register('pygame', pygame_mod_info)
        else:
            _hub.kengi_inj.set('pygame', pygame_mod_info)  # manually set the module, instead of using the injector

    __getattr__('legacy').legacyinit(gfc_mode)


def get_surface():
    return __getattr__('core').get_screen()


def flip():
    __getattr__('core').display_update()


def quit():
    __getattr__('legacy').old_cleanup()


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
    global init_done
    if init_done:
        return getattr(_hub, targ_sm_name)
    else:
        raise AttributeError(f"kengi cannot load {targ_sm_name}, the engine is not init yet!")
