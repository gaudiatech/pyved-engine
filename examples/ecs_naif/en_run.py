import pyved_engine as pyv
from demo_entities import Player
from demo_systems import SysInput, SysEntityMover, SysView2D


pyv.bootstrap_e()
# global vars
clock = None
game_systems = pyv.SystemManager()


def init_game():
    global clock, game_systems
    pyv.init(pyv.RETRO_MODE, maxfps=45, caption='my game (ECS fashion)')
    clock = pyv.vars.game_ticker

    # -----------------------
    #  Declare the pool of entities + all game systems
    # -----------------------
    entity_pool = pyv.EntityManager()
    _player = Player(
        x=128, y=32,
        max_hp=125,
        li_perks=['toughGuy', 'kamikaze'],
    )
    entity_pool.add(_player)

    game_systems.declare_systems([  # Instantiate all systems!
        SysInput(entity_pool),
        SysEntityMover(entity_pool),
        SysView2D(entity_pool, pyv.get_surface())
    ])


def ecs_std_game_loop():
    """
    here's THE STANDARDIZED way to implement the game loop
    (it's in the procedural format) when using the ECS pattern...
    """
    game_systems.init_all()
    while not game_systems['SysInput'].gameover:  # the game loop per se
        game_systems.proc_all()
        pyv.flip()
        clock.tick(pyv.vars.max_fps)
    game_systems.cleanup_all()


if __name__ == '__main__':
    print('Hint: Press SPACE to change the player gfx')
    init_game()
    ecs_std_game_loop()
