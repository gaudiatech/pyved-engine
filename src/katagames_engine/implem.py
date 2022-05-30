from . import _hub as hub

from .Injector import Injector
from ._BaseGameState import BaseGameState
from .__version__ import ENGI_VERSION
from .util import underscore_format, camel_case_format
from .foundation import defs
from .foundation import shared  # must keep this line /!\ see web vm

from .ifaces.pygame import PygameIface
from . import palettes

from .modes import GameModeMger, BaseGameMode


ver = ENGI_VERSION
pygame = PygameIface()
one_plus_init = False
_active_state = False


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
    global pygame, one_plus_init
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

    # dry import
    return get_injector()['pygame']


def init(gfc_mode='hd', caption=None, maxfps=60, screen_dim=None):
    global _active_state
    bootstrap_e()
    _active_state = True
    get_injector()['core'].init_e2(gfc_mode, caption, maxfps, screen_dim)


def get_surface():
    return get_injector()['core'].get_screen()


def flip():
    return get_injector()['core'].display_update()


def quit():
    global _active_state

    if _active_state:
        get_injector()['event'].EventManager.instance().hard_reset()

        get_injector()['event'].CogObj.reset_class_state()

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
