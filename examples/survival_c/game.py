import random

import gl_vars
import pyved_engine as pyv
import systems


MAX_FPS = 45
SCR_SIZE = (800, 600)
NZ = 8


def init_game():
    # here only to ensure that pyv is able to dynamically load Add-ons
    # print('Test the hub:')
    # for _ in range(3):
    #     obj = pyv.tabletop.StandardCard.at_random()
    #     print('    ', obj)
    # --- done testing!

    pyv.vars.screen = pyv.create_screen(SCR_SIZE)
    pyv.vars.clock = pyv.create_clock()

    # Define archetype
    pyv.define_archetype("Zombie", ["Position2d", "Health", "Color"])
    pyv.define_archetype("Player", ["Position2d", "Speed", "Gun", "Gfx"])

    # Create zombies
    zombies = [None] * NZ
    for i in range(NZ):
        zombies[i] = pyv.new_from_archetype("Zombie")
        pyv.initialize_entity(zombies[i], {"Position2d": (random.randint(100, 700), random.randint(100, 500)),
                                           "Health": random.randint(50, 100),
                                           "Color": (
                                               random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))})

    # Create player
    player = pyv.new_from_archetype("Player")
    pyv.initialize_entity(
        player,
        {
            "Position2d": (400, 300),
            "Speed": [0, 0],
            "Gun": {
                "dAngle": 0.0,
                "Angle": 0,
                "Damage": 10
            },
            "Gfx": {
                "Style": 0,
                "Spritesheet": pyv.load_spritesheet('topdown-shooter-spritesheet.png', (32, 32), ck='black')
            }
        }
    )

    # Add systems to the ECS
    pyv.bulk_add_systems(systems)


def run_zombie_demo():
    init_game()  # Game setup

    while gl_vars.running:
        for event in pyv.fetch_events():
            if event.type == pyv.QUIT:
                gl_vars.running = False

        # Run systems
        pyv.systems_proc()

        # Render game graphics
        pyv.flip()
        pyv.vars.clock.tick(MAX_FPS)


if __name__ == '__main__':
    pyv.init()
    run_zombie_demo()
    pyv.close_game()
    print('clean exit')
