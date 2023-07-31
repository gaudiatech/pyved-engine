"""
+----------------------------------------------------+
| Pyv - a pythonic 2d Game Engine                    |
| Our motto ~ Never slow down the innovation         |
|                                                    |
| https://github.com/gaudiatech/pyved-engine         |
| an open-source project started by GAUDIA TECH INC. |
|                                                    |
| Main author is Thomas Iwaszko a.k.a. moonbak       |
| (github.com/wkta) - Contact thomas.iw@kata.games   |
+----------------------------------------------------+
"""
from . import _hub
from .api import *
from . import vars


def get_version():
    return vars.ENGINE_VERSION_STR


# the basic API is expanded via our special "hub" component
def __getattr__(attr_name):
    if attr_name in ('ver', 'vernum'):
        return get_version()
    return getattr(_hub, attr_name)
