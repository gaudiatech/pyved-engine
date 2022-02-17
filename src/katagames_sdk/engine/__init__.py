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
import importlib

from . import legacy as _eng_legacy

from . import cgmconf

# TODO transition to:
# from ._carrefour import *
# from .boilerplate import gfx_updater as _updater
# from .boilerplate.BaseGameState import BaseGameState
from ..capsule.engine_ground.BaseGameState import BaseGameState
from .foundation import gfx_updater as _updater
from ..capsule.struct.misc import Stack

# - required
from .foundation.events import CogObject, EventReceiver, EngineEvTypes, CgmEvent, EventManager
from .foundation.defs import enum_for_custom_event_types

# gere extensions
_available_sub_modules = {
    'pygame': 'pygame',
    'anim': '..ext_anim',
    'isometric': '..ext_isometric'
}
_dep_cache = dict()
_flag_submodule_import = False


# gere states
class DummyState(BaseGameState):
    def __init__(self, ident, name):
        super().__init__(ident, name)

    def enter(self):
        print('entree dummy state')

    def release(self):
        print('release dummy state')


_curr_state = DummyState(-1, 'dummy_gs')
_loaded_states = {
    -1: _curr_state
}
state_stack = Stack()


def init(gfc_mode='hd', ext_module_asso=None):
    """
    :param gfc_mode:
    :param ext_module_asso: submodule name <> py module path
    """
    global _available_sub_modules, state_stack
    if ext_module_asso is not None:
        _available_sub_modules.update(ext_module_asso)

    _pygme = _lazy_import('pygame')
    cgmconf.pygame = _pygme
    _eng_legacy.legacyinit(_pygme, gfc_mode)
    _new_state(-1)


def declare_states(assoc_code_gs, new_state_id=None):
    global _loaded_states
    print('declaring states...')
    print(str(assoc_code_gs))
    print()

    # verif
    for ke, gs in assoc_code_gs.items():
        if ke in _loaded_states.keys():
            print('[Warning] gamestate code {} was already taken. Overriding state(risky)...'.format(ke))
            del _loaded_states[ke]
    _loaded_states.update(assoc_code_gs)
    # can change state instant
    if new_state_id is not None:
        print('wish new state:'+str(new_state_id))
        _new_state(new_state_id)


def _new_state(gs_code):
    global _curr_state, state_stack, _loaded_states

    print('new state call')
    print(gs_code)
    print(str(_loaded_states))

    _curr_state.release()
    state_stack.pop()

    state_stack.push(gs_code)
    _loaded_states[gs_code].enter()


def submodule_hacking(submodule_name, py_module):
    global _dep_cache, _flag_submodule_import
    if _flag_submodule_import:
        print('*** warning, submodule hacking done while some modules already loaded, this is risky! ***')
        print('prefer hacking before any loading (forced cache clear now...)')
    _dep_cache[submodule_name] = py_module
    print('submodule_hacking({}) -> ok'.format(submodule_name))


# implementing lazy, cached submodule import operation
def _lazy_import(name):
    global _available_sub_modules, _dep_cache, _flag_submodule_import
    if name not in _dep_cache:
        if name in _available_sub_modules.keys():
            _flag_submodule_import = True
            target_mod = _available_sub_modules[name]
            _dep_cache[name] = importlib.import_module(target_mod, __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return _dep_cache[name]


def __getattr__(name):
    return _lazy_import(name)


# -------------------------------------
#  METIER
# -------------------------------------
# you should call: kataen.EventManager.instance() instead
# def get_ev_manager():
#    return _eng_legacy.kevent.gl_unique_manager


def get_screen():
    return cgmconf.screen


def get_game_ctrl():
    return _eng_legacy.retrieve_game_ctrl()


def display_update():
    _updater.display_update()


# deprecated
def runs_in_web():
    return cgmconf.runs_in_web


def cleanup():
    _eng_legacy.cleanup()
