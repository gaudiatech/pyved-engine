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
from ._BaseGameState import BaseGameState
from .__version__ import ENGI_VERSION
from ._util import underscore_format, camel_case_format
from .foundation import defs
from .pygame_iface import PygameIface


ver = ENGI_VERSION
# pygame = PygameIface()
init_done = False


def init(gfc_mode='hd'):
    # global pygame
    global init_done
    if init_done:
        raise RuntimeError('dont init two times')
    init_done = True

    _hub.kengi_inj.register('pygame', 'pygame')  # lets use the genuine pygame lib, from now on
    # del pygame
    _hub.legacy.legacyinit(gfc_mode)


def get_surface():
    return _hub.core.get_screen()


def flip():
    _hub.core.display_update()


def quit():
    _hub.legacy.old_cleanup()


def set_package_arg(parg):
    _hub.Injector.package_arg = parg
    print('new package_arg set:', parg)


def plugin_bind(extname, pypath):
    _hub.kengi_inj.register_plugin(extname, pypath)


def bulk_plugin_bind_op(assoc_extname_pypath):
    for ename, pypath in assoc_extname_pypath.items():
        _hub.kengi_inj.register_plugin(ename, pypath)


def __getattr__(targ_sm_name):
    try:
        return getattr(_hub, targ_sm_name)
    except AttributeError:
        raise AttributeError("kengi has no attribute '{}'".format(targ_sm_name))
