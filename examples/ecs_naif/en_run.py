import pyved_engine as pyv
from demo_entities import Player
from demo_systems import SysInput, SysEntityMover, SysView2D


pyv.bootstrap_e()
pygame = pyv.pygame


def launch_game():
    # init imported pygame modules
    # pygame.init()
    pyv.init(1)

    pygame.display.set_caption('my game (ECS fashion)')
    # screen = pygame.display.set_mode((800, 500))
    clock = pygame.time.Clock()

    # declare pool of entities + all game systems
    entity_pool = pyv.EntityManager()
    _player = Player(
        x=128, y=32,
        max_hp=125,
        li_perks=['toughGuy', 'kamikaze'],
    )
    entity_pool.add(_player)

    game_systems = pyv.SystemManager([  # Instantiate all systems!
        SysInput(entity_pool),
        SysEntityMover(entity_pool),
        SysView2D(entity_pool, pyv.get_surface())
    ])

    # -------
    # STANDARDIZED launch game + game loop, here it's the procedural format
    game_systems.init_all()

    while not game_systems['SysInput'].gameover:  # game loop per se
        game_systems.proc_all()

        pyv.flip()
        clock.tick_busy_loop(pyv.config.MAXFPS)

    game_systems.cleanup_all()


if __name__ == '__main__':
    launch_game()
