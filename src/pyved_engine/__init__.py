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
from . import pe_vars as defs
from .EngineRouter import EngineRouter
from .Singleton import Singleton
from ._classes import *
from .compo import gfx
from .compo import vscreen  # deprecated
from .compo.GameTpl import GameTpl  # legacy cls
from .foundation.events import Emitter, EvListener, EngineEvTypes


_stored_kbackend = None
defs.weblib_sig = _backend_name = ''  # deprec.


def set_webbackend_type(xval):
    global _backend_name
    vars.weblib_sig = _backend_name = xval
    vars.backend_name = 'web'
