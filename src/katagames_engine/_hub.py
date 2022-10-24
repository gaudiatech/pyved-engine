"""
Keep this file separate from __init__.py!
its important, bc all sub-modules in kengi may import _hub
in order to refer to other dependencies/sub-modules
"""
from .Injector import Injector


kengi_inj = Injector({
    'ai': '.looparts.ai',
    'anim': '.looparts.anim',
    'ascii': '.looparts.ascii',
    'demolib': '.looparts.demolib',
    'polarbear': '.looparts.polarbear',
    'console': '.looparts.console',
    'gui': '.looparts.gui',
    'legacy': '.looparts.legacy',
    'tabletop': '.looparts.tabletop',
    'sysconsole': '.looparts.sysconsole',

    # nota bene: pygame is dynamically added to this dict,
    # its done elsewhere
    # 'tmx': '.looparts.tmx',

    'rogue': '.looparts.rogue',
    'terrain': '.looparts.terrain',
})


def __getattr__(targ_sm_name):
    if targ_sm_name in kengi_inj:
        return kengi_inj[targ_sm_name]
    else:
        raise AttributeError(f"kengi has no attribute named {targ_sm_name}")
