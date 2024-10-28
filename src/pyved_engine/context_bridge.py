import importlib as _importlib

from . import pal  # link to palette options
from ._ecs import all_entities, find_by_components, find_by_archetype, archetype_of, define_archetype, init_entity, \
    new_from_archetype, bulk_add_systems, systems_proc, delete_entity, wipe_entities
from ._utility import *  # dice rolls
from .api import curr_state, draw_polygon, draw_line, declare_game_states, enum, enum_from_n, game_events_enum, \
    get_ev_manager, get_surface, get_pressed_keys, bootstrap_e, declare_begin, declare_update, declare_end, \
    preload_assets, run_game, init, close_game, draw_rect, draw_circle, flip, get_gs_obj, new_font_obj, new_rect_obj
from .compo.GameTpl import GameTpl  # legacy cls
from .highlevel_functions import my_enum


# - define the full engine API for end users!
__all__ = [
    # - API of the Legacy ECS implementation

    # this may be superseded soon by the usage of "esper" as a game bundle dependency
    # for modern projects
    # But we keep this info as long as required so old game demos(roguelike, Breakout, etc)
    # need to be functional
    # misc:
    'pal',
    'GameTpl',

    # part: legacy ECS (that can still be used today)
    'all_entities',
    'archetype_of',
    'bulk_add_systems',
    'define_archetype',
    'delete_entity',
    'find_by_archetype',
    'find_by_components',
    'init_entity',
    'new_from_archetype',
    'systems_proc',
    'wipe_entities',

    # dice rolls
    'droll',
    'droll_4',
    'droll_8',
    'droll_10',
    'droll_12',
    'droll_20',
    'droll_100',
    'custom_droll',

    # other
    'get_gs_obj',

    'bootstrap_e',
    'bulk_add_systems',
    'close_game',
    'curr_state',
    'declare_begin',
    'declare_end',
    'declare_game_states',
    'declare_update',
    'define_archetype',
    'delete_entity',
    'draw_circle',
    'draw_line',
    'draw_polygon',
    'draw_rect',

    'new_font_obj',
    'new_rect_obj',

    'engine_activation',
    'engine_init',
    'enum',
    'enum_from_n',
    'find_by_archetype',
    'find_by_components',
    'flip',
    'game_events_enum',
    'get_ev_manager',
    'get_pressed_keys',
    'get_surface',
    'init',
    'init_entity',
    'machin',
    'my_enum',
    'new_from_archetype',
    'preload_assets',
    'run_game',
    'systems_proc'
]


#  + system +
# ------------------------
def _bind_implementation(adhoc_module):
    globals().update({
        'engine_init': adhoc_module.engine_init,
        'machin': adhoc_module.machin,
        'flip': adhoc_module.flip
    })


def engine_activation(mode: str, specific_context_implem=None):
    m = specific_context_implem if specific_context_implem else _importlib.import_module(
        '.local_context', 'pyved_engine'
    )
    # let us bind to a context implementation
    _bind_implementation(m)
    # rest of the procedure
    engine_init(mode)
    # for testing purpos only:
    machin()


# Declare func signatures for functions that DO DEPEND on the context ;
# functions corresponding to the 1st part of the Engine public API
# ------------------------
def engine_init(mode: str):
    print(mode)
    raise NotImplementedError


def machin():
    raise NotImplementedError
