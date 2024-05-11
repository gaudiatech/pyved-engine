import importlib as _importlib
# Let's fetch implementations
# (...that are INDEPENDANT from context)
# corresponding to the 2nd part of the Engine public API
# ------------------------
from .highlevel_functions import my_enum
from .api import curr_state, draw_polygon, draw_line, declare_game_states, enum, enum_from_n, game_events_enum,\
    get_ev_manager, get_surface, get_pressed_keys, close_game, bootstrap_e, declare_begin, declare_update, declare_end,\
    preload_assets, run_game, init, draw_rect, draw_circle, flip
from ._ecs import all_entities, find_by_components, find_by_archetype, archetype_of, define_archetype, init_entity,\
    new_from_archetype, bulk_add_systems, systems_proc, delete_entity


# - define the full engine API for end users!
__all__ = [
    'all_entities',
    'archetype_of',
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
