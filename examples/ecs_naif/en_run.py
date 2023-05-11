import pygame

import katagames_engine as pyv
from en_entities import Player
from en_systems import SysInput, SysEntityMover, SysGraphicalRepr


# ---
def run_game():
    tester = Player(
        x=0, y=256, max_hp=125, hp=None, li_perks=['toughGuy', 'kamikaze'],
        vx=0.0, vy=0.0
    )
    print(tester)

    pygame.init()  # init all imported pygame modules
    pygame.display.set_caption('Pong')
    screen = pygame.display.set_mode((800, 500))  # w h
    clock = pygame.time.Clock()

    entities_mger = pyv.EntityManager()
    entities_mger.add(
        tester
    )

    system_manager = pyv.SystemManager([
        SysInput(entities_mger),
        SysEntityMover(entities_mger),
        SysGraphicalRepr(entities_mger, screen)
    ])

    system_manager.init_all()

    # game_state_info: GameStateInfo = next(entities.get_by_class(GameStateInfo))
    # while game_state_info.play:
    #    clock.tick_busy_loop(60)  # tick_busy_loop точный + ест проц, tick грубый + не ест проц
    #    system_manager.update_systems()
    #    pygame.display.flip()  # draw changes on screen

    while not system_manager['SysInput'].gameover:
        system_manager.proc_all()
        pygame.display.flip()
        clock.tick_busy_loop(60)

    system_manager.cleanup_all()
    print('All Systems stopped')


run_game()
