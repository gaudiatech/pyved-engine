"""
goal of this file is to define the full engine API for end users...
But also specialize the API implementation based on the exec. context
"""
import importlib as _importlib
from . import _hub
# from ._hub import PyModulePromise, Injector, _kengi_inj
from . import dep_linking
from .utils._ecs import all_entities, find_by_components, find_by_archetype, archetype_of, define_archetype, init_entity, \
    new_from_archetype, bulk_add_systems, systems_proc, delete_entity, wipe_entities
# from .gamedev_api.highlevel import init, flip, close_game


# previously the pyved-engine was defined like this:
# TODO
# i hope to convert it to an abstract class

# __all__ = [
#     # const
#     'HIGH_RES_MODE', 'LOW_RES_MODE', 'RETRO_MODE',
#
#     'time',
#     'play_sound', 'stop_sound',
#
#     # newest gamedev API (2024-10)
#     'declare_evs', 'set_debug_flag',
#     'new_actor', 'del_actor', 'id_actor',
#     'peek', 'trigger',
#     'post_ev', 'process_evq',
#     'get_scene', 'set_scene', 'ls_scenes',
#     'DEFAULT_SCENE',
#
#     # misc:
#     #'PyModulePromise', 'Injector',
#     'pal',
#     'GameTpl',
#     'engine_activation',
#
#     # <legacy> core engine functions
#     'get_game_ctrl',
#     'get_ready_flag',
#
#     # <legacy> ECS, can still be used today but using the 'esper' ECS plugin2.0 is the preferred way
#     'all_entities',
#     'archetype_of',
#     'bulk_add_systems',
#     'define_archetype',
#     'delete_entity',
#     'find_by_archetype',
#     'find_by_components',
#     'init_entity',
#     'new_from_archetype',
#     'systems_proc',
#     'wipe_entities',
#
#     # other
#     'declare_game_states',
#     'enum',
#     'enum_from_n',
#     'game_events_enum',
#
#     'get_gs_obj',
#
#     'bootstrap_e',
#     'bulk_add_systems',
#     'close_game',
#     'curr_state',
#     'declare_begin',
#     'declare_end',
#     'declare_update',
#     'draw_circle',
#     'draw_line',
#     'draw_polygon',
#     'draw_rect',
#     'new_font_obj',
#     'new_rect_obj',
#
#     'engine_init',
#     'flip',
#     'get_ev_manager',
#     'get_pressed_keys',
#     'get_surface',
#     'init',
#     'init_entity',
#     'new_from_archetype',
#     'preload_assets',
#     'run_game',
#     'systems_proc',
#     'get_mouse_coords',
#
#     'surface_create',
#     'surface_rotate',
#     'create_clock'
# ]


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
