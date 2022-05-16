"""
Keep this file separate from __init__.py!
its important, bc all sub-modules in kengi may import _hub
in order to refer to other dependencies/sub-modules
"""
from .Injector import Injector


kengi_inj = Injector({
    'anim': '._sm_shelf.anim',
    'ascii': '._sm_shelf.ascii',
    'polarbear': '._sm_shelf.polarbear',
    'terrain': '._sm_shelf.terrain',
    'console': '._sm_shelf.console',
    'core': '._sm_shelf.core',
    'event': '._sm_shelf.event',
    'gui': '._sm_shelf.gui',
    'isometric': '._sm_shelf.isometric',
    'legacy': '._sm_shelf.legacy',
    'network': '._sm_shelf.network',

    # nota bene: pygame is dynamically added to this dict,
    # its done elsewhere

    'struct': '._sm_shelf.struct',
    'tmx': '._sm_shelf.tmx',
})


def __getattr__(targ_sm_name):
    if targ_sm_name in kengi_inj:
        return kengi_inj[targ_sm_name]
    else:
        raise AttributeError(f"kengi has no attribute named {targ_sm_name}")
