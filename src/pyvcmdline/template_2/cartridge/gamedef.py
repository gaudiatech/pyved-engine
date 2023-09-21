import os

from . import pimodules
from . import shared
from . import systems
from .World import World
from .classes import Camera


pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pygame = pyv.pygame
ts_prev_frame = None


@pyv.declare_begin
def troid_init(vms=None):
    pyv.init()
    screen = pyv.get_surface()
    shared.screen = screen
    pyv.define_archetype('player', (
        'speed', 'accel_y', 'gravity', 'lower_block', 'body', 'camera', 'controls'
    ))
    pyv.define_archetype('block', ['body', ])
    pyv.define_archetype('mob_block', ['body', 'speed', 'bounds', 'horz_flag', ])

    world = World(2128.0, 1255.0)
    world.load_map('my_map')
    shared.world = world
    world.add_game_obj(
        {'key': 'origin'}
    )
    camera = Camera([-280, -280], world)

    world.create_avatar(camera)
    pyv.bulk_add_systems(systems)


@pyv.declare_update
def troid_update(timeinfo):
    shared.t_now=timeinfo
    pyv.systems_proc(pyv.all_entities(), None)
    pyv.flip()


@pyv.declare_end
def troid_exit(vms=None):
    pyv.quit()
