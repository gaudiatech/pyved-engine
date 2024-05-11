"""
+----------------------------------------------------+
| Pyv - a pythonic 2d Game Engine                    |
| Our motto ~ Never slow down the innovation         |
|                                                    |
| https://github.com/gaudiatech/pyved-engine         |
| an open-source project started by GAUDIA TECH INC. |
|                                                    |
| Main author is Thomas EDER a.k.a. moonbak       |
| (github.com/wkta) - Contact thomas.iw@kata.games   |
+----------------------------------------------------+
"""
from . import _hub
hub = _hub

from .context_bridge import *  # api is already packed in this file
from . import custom_struct as struct
from .core.events import Emitter, EvListener, EngineEvTypes
from ._classes import BaseGameState
from .Singleton import Singleton
from .compo import gfx

from . import vars

# deprecated
from .compo import vscreen

# TODO remove this when we can
# ive kept it for retro-compatibility with projects that target pyv v23.6a1
# such as demos/ecs_naif or the very early stage pyved ships-with-GUI editor
from ._ecs_pattern import entity, component, System, SystemManager, EntityManager

# useful ALIAS! (webctx)
defs = vars


def get_version():
    return vars.ENGINE_VERSION_STR


_stored_kbackend = None
# deprec.
vars.weblib_sig = _backend_name = ''
quit = close_game


def set_webbackend_type(xval):
    global _backend_name
    vars.weblib_sig = _backend_name = xval
    vars.backend_name = 'web'


# the basic API is expanded via our special "hub" component
def __getattr__(attr_name):
    if attr_name in ('ver', 'vernum'):
        return get_version()
    return getattr(_hub, attr_name)
