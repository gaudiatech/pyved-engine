"""
goal of this file is to define the full engine API for end users...
But also specialize the API implementation based on the exec. context
"""

import importlib as _importlib

from . import pal  # link to palette options
from ._ecs import all_entities, find_by_components, find_by_archetype, archetype_of, define_archetype, init_entity, \
    new_from_archetype, bulk_add_systems, systems_proc, delete_entity, wipe_entities
from ._utility import *  # dice rolls
from .compo.GameTpl import GameTpl  # legacy cls
from .gamedev_api.highlevel import *


__all__ = [
    # const
    'HIGH_RES_MODE', 'LOW_RES_MODE', 'RETRO_MODE',

    # misc:
    'new_actor', 'del_actor', 'get_curr_world', 'switch_world', 'post_ev', 'process_events',
    'pal',
    'GameTpl',

    'engine_activation',

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
    'declare_game_states',
    'enum',
    'enum_from_n',
    'game_events_enum',

    'get_gs_obj',

    'bootstrap_e',
    'bulk_add_systems',
    'close_game',
    'curr_state',
    'declare_begin',
    'declare_end',
    'declare_update',
    'draw_circle',
    'draw_line',
    'draw_polygon',
    'draw_rect',
    'new_font_obj',
    'new_rect_obj',

    'engine_init',
    'flip',
    'get_ev_manager',
    'get_pressed_keys',
    'get_surface',
    'init',
    'init_entity',
    'new_from_archetype',
    'preload_assets',
    'run_game',
    'systems_proc'
]


#  + system +
# ------------------------
def _bind_api_implem(adhoc_module):
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
    _bind_api_implem(m)
    # for testing purpose only:
    machin()
    # rest of the procedure
    engine_init(mode)


# Here we will declare only **function signatures**
# for functions that we expect to find in the engine but INDEED DEPEND
# on the run context...
# This is the 1st PART of the function list tied to the gamedev API
# ------------------------
def engine_init(mode: str):
    raise NotImplementedError


def machin():
    raise NotImplementedError
