from . import pimodules
from . import shared
from . import world


__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'rendering_sys',
    'physics_sys'
]

# aliases
pyv = pimodules.pyved_engine
pyv.bootstrap_e()
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.e_struct.BoolMatrix
tileset = None
pg = pyv.pygame


def pg_event_proces_sys():
    avpos = pyv.find_by_archetype('player')[0]['position']
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                avpos[1] -= 1
                shared.last_hit_key = "pg.K_UP"
            elif ev.key == pg.K_DOWN:
                avpos[1] += 1
                shared.last_hit_key = "pg.K_DOWN"

            elif ev.key == pg.K_LEFT:
                avpos[0] -= 1
                shared.last_hit_key = "pg.K_LEFT"

            elif ev.key == pg.K_RIGHT:
                avpos[0] += 1
                shared.last_hit_key = "pg.K_RIGHT"

            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


def world_generation_sys():
    pl_ent = pyv.find_by_archetype('player')[0]
    mobs = pyv.find_by_archetype('monster')

    if pl_ent['enter_new_map']:
        pl_ent['enter_new_map'] = False
        print('Level generation...')
        w, h = 24, 24
        shared.game_state["rm"] = pyv.rogue.RandomMaze(
            w, h, min_room_size=3, max_room_size=5)
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        pyv.find_by_archetype('player')[0]['position'] = shared.game_state["rm"].pick_walkable_cell()
        world._update_vision(pyv.find_by_archetype('player')[0]['position'][0], pyv.find_by_archetype('player')[0]['position'][1])
        shared.game_state["enemies_pos2type"].clear()
        for _ in range(5):
            c = shared.game_state['rm'].pick_walkable_cell()
            shared.game_state["enemies_pos2type"][tuple(c)] = 1  # all enemies type=1
            print(c)
            world.create_monster(c)


def rendering_sys():
    global tileset
    scr = shared.screen
    scr.fill(shared.WALL_COLOR)
    player = pyv.find_by_archetype('player')[0]
    monster = pyv.find_by_archetype('monster')

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


    if (player.position[0], player.position[1]) not in shared.walkable_cells:
        if shared.last_hit_key == "pg.K_RIGHT":
            player.position[0] -= 1
        elif shared.last_hit_key == "pg.K_LEFT":
            player.position[0] += 1
        elif shared.last_hit_key == "pg.K_UP":
            player.position[1] += 1
        elif shared.last_hit_key == "pg.K_DOWN":
            player.position[1] -= 1
    # ----------
    #  draw player/enemies
    # ----------
    av_i, av_j = pyv.find_by_archetype('player')[0]['position']

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)
    scr.blit(shared.AVATAR, (targx, targy, 32, 32))
    # ----- enemies
    for enemy_info in shared.game_state["enemies_pos2type"].items():
        pos, t = enemy_info
        if not shared.game_state['visibility_m'].get_val(*pos):
            continue
        en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
        scr.blit(shared.MONSTER, (en_i, en_j, 32, 32))


def physics_sys():
    player = pyv.find_by_archetype('player')[0]        
    monster = pyv.find_by_archetype('monster')
    for m in monster:
        if player.position == m.body:
            m.health_point -= player.damages
            if m.health_point < 0:
                pyv.delete_entity(m)
                d= shared.game_state["enemies_pos2type"]
                del d[(m.body[0], m.body[1])]
    
    

