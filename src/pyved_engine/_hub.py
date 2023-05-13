"""
Keep this file separate from __init__.py!
its important, bc all sub-modules in kengi may import _hub
in order to refer to other dependencies/sub-modules
"""
from .core import events

from .core.Injector import Injector as Injector


kengi_inj = Injector({
    'ai': '.looparts.ai',
    'demolib': '.looparts.demolib',
    'gui': '.looparts.gui',
    'isometric': '.looparts.isometric',
    'polarbear': '.looparts.polarbear',
    'tmx': '.looparts.tmx',
    'anim': '.looparts.anim',
    'ascii': '.looparts.ascii',
    'console': '.looparts.console',
    'rogue': '.looparts.rogue',
    'rpg': '.looparts.rpg',
    'sysconsole': '.looparts.sysconsole',
    'tabletop': '.looparts.tabletop',
    'terrain': '.looparts.terrain',
}, 'pyved_engine')


def __getattr__(targ_sm_name):
    if targ_sm_name in kengi_inj:
        return kengi_inj[targ_sm_name]
    else:
        raise AttributeError(f"kengi has no attribute named {targ_sm_name}")
