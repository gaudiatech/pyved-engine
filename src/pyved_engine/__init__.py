"""
+----------------------------------------------------+
| Pyv - a pythonic 2d Game Engine                    |
| Our motto ~ Never slow down the innovation         |
|                                                    |
| https://github.com/gaudiatech/pyved-engine         |
| an open-source project started by GAUDIA TECH INC. |
|                                                    |
| Main author is: Thomas I. EDER / moonbak           |
| (github.com/wkta) - Contact thomas@katagames.io    |
+----------------------------------------------------+
"""
from . import _hub
from .Singleton import Singleton
from ._classes import *
from .compo import gfx
from .compo import vscreen  # deprecated
from .compo.GameTpl import GameTpl  # legacy cls
from .foundation import legacy_evs  # we just copy the event system of pygame
from .foundation.events import Emitter, EvListener, EngineEvTypes
from .utils import vars as defs
from .EngineRouter import EngineRouter


# TODO remove this when we can
# ive kept it for retro-compatibility with projects that target pyv v23.6a1
# such as demos/ecs_naif or the very early stage pyved ships-with-GUI editor
from .utils._ecs_pattern import entity, component, System, SystemManager, EntityManager
from . import evsys0


_stored_kbackend = None
defs.weblib_sig = _backend_name = ''  # deprec.


def set_webbackend_type(xval):
    global _backend_name
    vars.weblib_sig = _backend_name = xval
    vars.backend_name = 'web'


# the basic API used to be expanded via our special "hub" component
# def __getattr__(attr_name):
#     if attr_name in ('ver', 'vernum'):
#         return get_version()
#     elif attr_name == 'Sprite':
#         return dep_linking.pygame.sprite.Sprite
#     elif attr_name == 'SpriteGroup':
#         return dep_linking.pygame.sprite.Group
#     elif attr_name == 'sprite_collision':
#         return dep_linking.pygame.sprite.spritecollide
#     return getattr(_hub, attr_name)
