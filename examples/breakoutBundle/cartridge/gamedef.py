from . import pimodules
from . import shared
from . import systems
from .world import world

pyv = pimodules.pyved_engine


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    screen = pyv.get_surface() 
    shared.screen = screen
    pyv.init(wcaption='Pyv Breaker')
    pyv.define_archetype('player', (
        'speed', 'controls', 'body'
    ))
    pyv.define_archetype('block', ('body', ))
    pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))
    world.create_player()
    world.create_ball()
    world.create_blocks()
    pyv.bulk_add_systems(systems)


@pyv.declare_update
def upd(time_info=None):
    pyv.systems_proc()
    pyv.flip()



@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')