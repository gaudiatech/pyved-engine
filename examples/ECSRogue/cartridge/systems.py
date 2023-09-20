import time
from . import shared
from . import pimodules
from . import world
import os

pyv = pimodules.pyved_engine
pyv.bootstrap_e()
BoolMatrx = pyv.e_struct.BoolMatrix

__all__ = [
    'controls_sys',
    'world_generation_sys',
    'rendering_sys',
    'gamectrl_sys'
]


def controls_sys(entities, components):
    pg = pyv.pygame

    player = pyv.find_by_archetype('player')
    activekeys = pg.key.get_pressed()


def world_generation_sys(entities, components):
    if pyv.find_by_archetype('player')[0]['enter_new_map']:
        pyv.find_by_archetype('player')[0]['enter_new_map'] = False
        print('Level generation...')
        w, h = 24, 24
        shared.game_state["rm"] = pyv.rogue.RandomMaze(
            w, h, min_room_size=3, max_room_size=5)
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        shared.game_state["player_pos"] = shared.game_state["rm"].pick_walkable_cell()
        pyv.find_by_archetype('player')[0]['body'] = shared.game_state["player_pos"]
        world._update_vision(shared.game_state["player_pos"][0],shared.game_state["player_pos"][1] )
        shared.game_state["enemies_pos2type"].clear()
        for _ in range(5):
            c = shared.game_state['rm'].pick_walkable_cell()
            shared.game_state["enemies_pos2type"][tuple(c)] = 1  # all enemies type=1
            


def rendering_sys(entities, components):
    scr = shared.screen

    scr.fill((0, 0, 0))


def gamectrl_sys(entities, components):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True
