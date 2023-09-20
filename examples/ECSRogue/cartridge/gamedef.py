from . import pimodules
from . import shared
from . import systems
from . import world

pyv = pimodules.pyved_engine

@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Roguata')
    screen = pyv.get_surface() 
    shared.screen = screen
    pyv.define_archetype('player', (
        'controls', 'body', 'damages', 'health_point', 'enter_new_map'
    ))
    pyv.define_archetype('wall', ('body', ))
    pyv.define_archetype('monster', ('body', 'damages', 'health_point'))
    pyv.define_archetype('exit', ('body', ))
    world.create_player()
    world.create_wall()
    world.create_exit()
    world.create_monster()
    world.init_images()
    pyv.bulk_add_systems(systems)


@pyv.declare_update
def upd(time_info=None):
    # pyv.vars.gameover=True
    pyv.systems_proc()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
