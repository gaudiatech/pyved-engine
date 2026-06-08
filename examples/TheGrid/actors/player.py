"""
we actors for the Roguelike here,
except from "maze" and "player" that have their own file
"""
from ..glvars import pyv
from .. import glvars


def new_player(new_position):
    # ---- anciennement ----
    # 'position': None,
    # 'controls': {'left': False, 'right': False, 'up': False, 'down': False},
    # 'damages': shared.PLAYER_DMG,
    # 'health_point': shared.PLAYER_HP,
    # 'enter_new_map': True

    data = {
        'pos': new_position,
        'hitpoints': glvars.avatar_hp,
        'future_pos': None
    }
    pyv.post_ev('player_spawn', pos=new_position)

    # -----------
    #  utils
    def change_hp(this, value):
        old_hp = this.hitpoints
        delta_str = str(value)
        this.hitpoints += value
        print(f' Player HEALTH {old_hp} ->{this.hitpoints} (hp change: {delta_str})')

        if this.hitpoints > glvars.HITPOINTS_CAP:
            this.hitpoints = glvars.HITPOINTS_CAP
            print('max hp reached, new value:', glvars.HITPOINTS_CAP)
        elif this.hitpoints <= 0:
            pyv.post_ev('player_death')
            print(' xOxOx ...player died... xOxOx ')
        # sync with glvars
        glvars.avatar_hp = this.hitpoints

    # -----------
    #  behavior
    def on_spawn(this, ev):
        this.pos = ev.pos
        pyv.post_ev('avatar_movement', pos=this.pos)

    def on_player_input(this, ev):
        # TODO collision contre murs pas tout à fait, ok. Sur la 1er level ca va, les autres ca bug
        if ev.dir not in ('right', 'down', 'left', 'up'):
            return
        directio = ev.dir

        # player = pyv.find_by_archetype('player')[0]
        # monsters = pyv.find_by_archetype('monster')  # TODO kick mobs? missing feat.
        # print(glvars.walkable_cells)
        future_pos = list(this.pos)
        deltas = {
            'right': (+1, 0),  # right
            'up': (0, -1),  # up
            'left': (-1, 0),  # left
            'down': (0, +1)  # down
        }
        future_pos[0] += deltas[directio][0]  # why this sign?
        future_pos[1] += deltas[directio][1]
        x = tuple(future_pos)
        if x not in glvars.walkable_cells:
            print('hitting a wall, takes time tho')
        else:
            this.pos = x
        pyv.post_ev('player_movement', pos=this.pos)

    def on_draw(this, ev):
        scr = ev.screen
        # >>> player = pyv.find_by_archetype('player')[0]
        # all_mobs = pyv.find_by_archetype('monster')
        # ----------
        #  draw player/enemies
        # ----------
        if this.pos is None:
            print('xx warning->pos is None')
            return
        av_i, av_j = this.pos
        exit_i, exit_j = 23, 20
        # exit_ent = pyv.find_by_archetype('exit')[0]
        # potion = pyv.find_by_archetype('potion')[0]
        # tuile = shared.TILESET.image_by_rank(912)

        # ->draw exit
        #if pyv.actor_state(glvars.ref_maze).visibility_map.get_val(exit_i, exit_j):
        #    scr.blit(glvars.tileset.image_by_rank(1092),
        #             (exit_i * glvars.CELL_SIDE, exit_j * glvars.CELL_SIDE, 32, 32))

        # ->draw potions
        # if shared.game_state['visibility_m'].get_val(*potion.position):
        # 	if potion.effect == 'Heal':
        # 		scrref.blit(shared.TILESET.image_by_rank(810),
        # 					(potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))
        # 	elif potion.effect == 'Poison':
        # 		scrref.blit(shared.TILESET.image_by_rank(810),
        # 					(potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))

        # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
        proj_function = lambda locali, localj: (locali * glvars.CELL_SIDE, localj * glvars.CELL_SIDE)
        targx, targy = proj_function(av_i, av_j)
        scr.blit(glvars.avatar_img, (targx, targy, 32, 32))
    # ----- enemies
    # for enemy_info in shared.game_state["enemies_pos2type"].items():
    # for mob_ent in all_mobs:
    # 	pos = mob_ent.position
    # 	# pos, t = enemy_info
    # 	if not shared.game_state['visibility_m'].get_val(*pos):
    # 		continue
    # 	en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
    # 	scrref.blit(shared.MONSTER, (en_i, en_j, 32, 32))

    return pyv.new_actor('player', locals())

print('x')
