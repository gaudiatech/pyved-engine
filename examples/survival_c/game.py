import random

import pyved_engine as pyv
import shared
import systems


@pyv.declare_begin
def prep_zombiegame():
    pyv.init()

    pyv.define_archetype("Zombie", ["Position2d", "Health", "Color"])
    pyv.define_archetype("Player", ["Position2d", "Speed", "Gun", "Gfx"])

    # Create zombies
    zombies = [None] * shared.NZ
    for i in range(shared.NZ):
        zombies[i] = pyv.new_from_archetype("Zombie")
        pyv.init_entity(
            zombies[i],
            {
                "Position2d": (random.randint(100, 700), random.randint(100, 500)),
                "Health": random.randint(50, 100),
                "Color": [random.randint(0, 255) for _ in range(3)]
            }
        )

    # Create player
    player = pyv.new_from_archetype("Player")
    pyv.init_entity(
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
    pyv.bulk_add_systems(systems)  # get any system found in module 'systems', add it to the ECS manager


@pyv.declare_update
def maj_zombiegame(into_t):
    for event in pyv.fetch_events():
        if event.type == pyv.QUIT:
            pyv.vars.gameover = True
    pyv.systems_proc()  # run everything described in systems


@pyv.declare_end
def zombie_gameover():
    pyv.close_game()


if __name__ == '__main__':
    pyv.run_game()
