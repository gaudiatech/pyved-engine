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
from . import struct
from . import tankui
from . import vars
from ._BaseGameState import BaseGameState
from ._ecs_pattern import entity, component, EntityManager, System, SystemManager
from ._hub import Injector
from .compo import gfx
from .compo import vscreen
from .compo.modes import GameModeMger, BaseGameMode
from .compo.vscreen import flip, proj_to_vscreen
from .core import events
from .core.events import Emitter, EvListener, EngineEvTypes, game_events_enum
from .foundation import defs
from .foundation.defs import STD_SCR_SIZE, KengiEv, Singleton
from .foundation.interfaces import PygameIface
from .util import underscore_format, camel_case_format

# expose all that exists within the pyv interface implementation!!
from ._pyv_implem import *  # check __all__ in the file
from .core_classes import *  # check the __all__ variable


config = core_classes.ConfigStorage


# ----------------------------
#  Related to lazy import
# ----------------------------
# this line was here to allow Code Inspection when using legacy API ...
# pyv.pygame.X  auto-completion etc.
# pygame = PygameIface()


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


def __getattr__(attr_name):
    if attr_name in ('ver', 'vernum'):
        return get_version()

    if attr_name == 'Sprite':
        return _hub.pygame.sprite.Sprite

    if get_ready_flag():
        return getattr(hub, attr_name)

    raise AttributeError(f"kengi cannot lazy load, it hasnt bootstrap yet! (user request: {attr_name})")
