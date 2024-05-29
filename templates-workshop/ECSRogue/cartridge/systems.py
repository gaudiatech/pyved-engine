import random

from . import pimodules
from . import shared
from . import world


__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'gamestate_update_sys',
    'rendering_sys',
    'physics_sys',
    'monster_ai_sys'
]


# aliases
pyv = pimodules.pyved_engine
pg = pyv.pygame
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.e_struct.BoolMatrix


# global vars
tileset = None
saved_player_pos = [None, None]


def pg_event_proces_sys():
    if shared.end_game_label0:
        for ev in pg.event.get():
            if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
        return
    avpos = pyv.find_by_archetype('player')[0]['position']
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                avpos[1] -= 1
                _player_push(1)
            elif ev.key == pg.K_DOWN:
                avpos[1] += 1
                _player_push(3)

            elif ev.key == pg.K_LEFT:
                avpos[0] -= 1
                _player_push(2)

            elif ev.key == pg.K_RIGHT:
                avpos[0] += 1
                _player_push(0)

            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


def world_generation_sys():
    pl_ent = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    potion = pyv.find_by_archetype('potion')[0]
    exit_ent = pyv.find_by_archetype('exit')[0]

    if pl_ent['enter_new_map']:
        pl_ent['enter_new_map'] = False
        print('Level generation...')

        w, h = 24, 24
        shared.random_maze = pyv.rogue.RandomMaze(w, h, min_room_size=3, max_room_size=5)
        # print(shared.game_state['rm'].blocking_map)

        # IMPORTANT: adding mobs comes before computing the visibility
        shared.game_state["enemies_pos2type"].clear()
        for monster in monsters:
            pyv.delete_entity(monster)
        for _ in range(5):
            tmp = shared.random_maze.pick_walkable_cell()
            pos_key = tuple(tmp)
            shared.game_state["enemies_pos2type"][pos_key] = 1  # all enemies type=1
            world.create_monster(tmp)

        # - comp. the visibility
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        shared.walkable_cells = []
        shared.game_state['visibility_m'].set_all(False)
        pyv.find_by_archetype('player')[0]['position'] = shared.random_maze.pick_walkable_cell()
        world.update_vision_and_mobs(
            pyv.find_by_archetype('player')[0]['position'][0],
            pyv.find_by_archetype('player')[0]['position'][1]
        )

        # add-on?
        while True:
            exitPos = shared.random_maze.pick_walkable_cell()
            if exitPos not in [pl_ent.position] + [monster.position for monster in monsters]:
                exit_ent.position = exitPos
                break

        while True:
            resultat = random.randint(0, 1)
            potionPos = shared.random_maze.pick_walkable_cell()
            if potionPos not in [pl_ent.position] + [monster.position for monster in monsters] + [exit_ent.position]:
                potion.position = potionPos
                if resultat == 0:
                    potion.effect = 'Heal'
                else:
                    potion.effect = 'Poison'
                break


def gamestate_update_sys():
    player = pyv.find_by_archetype('player')[0]
    classic_ftsize = 38
    if player.health_point <= 0 and (shared.end_game_label0 is None):
        ft = pyv.pygame.font.Font(None, classic_ftsize)
        shared.end_game_label0 = ft.render('Game Over', True, (255, 255, 255), 'black')
        shared.end_game_label1 = ft.render(f'You reached Level : {shared.level_count}', True, (255, 255, 255), 'black')


def rendering_sys():
    global tileset
    scr = shared.screen
    scr.fill(shared.WALL_COLOR)

    # ----------
    #  draw tiles
    # ----------
    nw_corner = (0, 0)
    tmp_r4 = [None, None, None, None]
    tuile = shared.TILESET.image_by_rank(912)
    dim = world.get_terrain().get_size()
    for i in range(dim[0]):
        for j in range(dim[1]):
            # ignoring walls
            tmp = world.get_terrain().get_val(i, j)
            if tmp is None:
                continue

            tmp_r4[0], tmp_r4[1] = nw_corner
            tmp_r4[0] += i * shared.CELL_SIDE
            tmp_r4[1] += j * shared.CELL_SIDE
            tmp_r4[2] = tmp_r4[3] = shared.CELL_SIDE
            if not world.can_see((i, j)):  # hidden cell

                pg.draw.rect(scr, shared.HIDDEN_CELL_COLOR, tmp_r4)
            else:  # visible tile
                scr.blit(tuile, tmp_r4)
                shared.walkable_cells.append((i, j))

    if shared.end_game_label0:
        lw, lh = shared.end_game_label0.get_size()
        scr.blit(
            shared.end_game_label0, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 3)
        )
        scr.blit(
            shared.end_game_label1, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 2)
        )
        return
    _draw_all_mobs(scr)


def physics_sys():
    """
    implements the monster attack mechanic
    + it also proc any effect on the player based on what happened (potion, exit door etc)
    """
    player = pyv.find_by_archetype('player')[0]
    monster = pyv.find_by_archetype('monster')
    exit_ent = pyv.find_by_archetype('exit')[0]
    potion = pyv.find_by_archetype('potion')[0]

    for m in monster:
        if m.position == player.position:
            m.health_point -= player.damages
            player.health_point -= m.damages
            if m.health_point < 0:
                pyv.delete_entity(m)

    if player.position == exit_ent.position:
        player['enter_new_map'] = True
        shared.level_count += 1
        print('YOU REACHED LEVEL : ' + str(shared.level_count))

    if player.position == potion.position:
        if potion.effect == 'Heal':
            player.health_point = 100
            print(player.health_point)
            potion.effect = 'disabled'
        elif potion.effect == 'Poison':
            player.health_point -= 20
            print(player.health_point)
            potion.effect = 'disabled'


def monster_ai_sys():
    global saved_player_pos
    i, j = saved_player_pos
    player = pyv.find_by_archetype('player')[0]
    curr_pos = player.position

    if (i is None) or curr_pos[0] != i or curr_pos[1] != j:
        # position has changed!
        saved_player_pos[0], saved_player_pos[1] = curr_pos
        blockmap = shared.random_maze.blocking_map
        allmobs = pyv.find_by_archetype('monster')
        for mob_ent in allmobs:
            if not mob_ent.active:
                pass
            else:
                pathfinding_result = pyv.terrain.DijkstraPathfinder.find_path(
                    blockmap, mob_ent.position, player.position
                )
                new_pos = pathfinding_result[1]  # index 1 --> 1 step forward!
                print('pathfind: mob selects', new_pos)
                mob_ent.position[0], mob_ent.position[1] = new_pos  # TODO a proper "kick the player" feat.


# ----------------------------
#  private/utility functions
# ----------------------------
def _draw_all_mobs(scrref):
    player = pyv.find_by_archetype('player')[0]
    all_mobs = pyv.find_by_archetype('monster')
    # ----------
    #  draw player/enemies
    # ----------
    av_i, av_j = player['position']
    exit_ent = pyv.find_by_archetype('exit')[0]
    potion = pyv.find_by_archetype('potion')[0]
    tuile = shared.TILESET.image_by_rank(912)
    if shared.game_state['visibility_m'].get_val(*exit_ent.position):
        scrref.blit(shared.TILESET.image_by_rank(1092),
                    (exit_ent.position[0] * shared.CELL_SIDE, exit_ent.position[1] * shared.CELL_SIDE, 32, 32))

    if shared.game_state['visibility_m'].get_val(*potion.position):
        if potion.effect == 'Heal':
            scrref.blit(shared.TILESET.image_by_rank(810),
                        (potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))
        elif potion.effect == 'Poison':
            scrref.blit(shared.TILESET.image_by_rank(810),
                        (potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)
    scrref.blit(shared.AVATAR, (targx, targy, 32, 32))
    # ----- enemies
    # for enemy_info in shared.game_state["enemies_pos2type"].items():
    for mob_ent in all_mobs:
        pos = mob_ent.position
        # pos, t = enemy_info
        if not shared.game_state['visibility_m'].get_val(*pos):
            continue
        en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
        scrref.blit(shared.MONSTER, (en_i, en_j, 32, 32))


def _player_push(directio):
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')  # TODO kick mob feat. here?
    if (player.position[0], player.position[1]) not in shared.walkable_cells:
        print('kick')
        deltas = {
            0: (+1, 0),
            1: (0, -1),
            2: (-1, 0),
            3: (0, +1)
        }
        player.position[0] -= deltas[directio][0]
        player.position[1] -= deltas[directio][1]
    # Update player vision
    world.update_vision_and_mobs(player.position[0], player.position[1])
