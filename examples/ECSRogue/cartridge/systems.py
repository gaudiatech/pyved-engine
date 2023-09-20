from . import pimodules
from . import shared
from . import world


__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'rendering_sys'
]

# aliases
pyv = pimodules.pyved_engine
pyv.bootstrap_e()
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.e_struct.BoolMatrix
tileset = None


def pg_event_proces_sys():
    pg = pyv.pygame
    avpos = shared.game_state["player_pos"]
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                avpos[1] -= 1
            elif ev.key == pg.K_DOWN:
                avpos[1] += 1
            elif ev.key == pg.K_LEFT:
                avpos[0] -= 1
            elif ev.key == pg.K_RIGHT:
                avpos[0] += 1
            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


def world_generation_sys():
    pl_ent = pyv.find_by_archetype('player')[0]
    if pl_ent['enter_new_map']:
        pl_ent['enter_new_map'] = False

        print('Level generation...')
        w, h = 24, 24
        shared.game_state["rm"] = pyv.rogue.RandomMaze(
            w, h, min_room_size=3, max_room_size=5)
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        shared.game_state["player_pos"] = shared.game_state["rm"].pick_walkable_cell()
        pyv.find_by_archetype('player')[0]['body'] = shared.game_state["player_pos"]
        world._update_vision(shared.game_state["player_pos"][0], shared.game_state["player_pos"][1])
        shared.game_state["enemies_pos2type"].clear()
        for _ in range(5):
            c = shared.game_state['rm'].pick_walkable_cell()
            shared.game_state["enemies_pos2type"][tuple(c)] = 1  # all enemies type=1


def rendering_sys():
    global tileset
    scr = shared.screen
    scr.fill(shared.WALL_COLOR)
    player = pyv.find_by_archetype('player')[0]

    # TODO optimize: on peut améliorer le placement de ce bloc (entre {}) qui fait init. sur valeur tileset
    # voir où il est judicieux de le placer dans le code!  {
    # --- en attendant : late init.
    if tileset is None:
        img = pyv.vars.images['tileset']
        tileset = Sprsheet(img, 2)  # use upscaling x2
        tileset.set_infos(shared.GRID_REZ)
    # }

    # ----------
    #  draw tiles
    # ----------
    nw_corner = (0, 0)
    tmp_r4 = [None, None, None, None]
    tuile = tileset.image_by_rank(912)
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

            # TODO :faut retablir le Fog-of-war
            # if not world.mod.can_see((i, j)):  # hidden cell
            #     pygame.draw.rect(scr, self.HIDDEN_CELL_COLOR, tmp_r4)
            # else:  # visible tile
            #     scr.blit(tuile, tmp_r4)

            # --- en attendant que ce soit fait, on va blit la tuile, systématiquement:
            scr.blit(tuile, tmp_r4)

    # ----------
    #  draw player/enemies
    # ----------
    av_i, av_j = shared.game_state['player_pos']

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)

    # TODO faut retrouver l'img correspondante a l'avatar pr retablir cette ligne
    # scr.blit(self.avatar_apparence, (targx, targy, 32, 32))
    # --- en attendant: du code temporaire sur 4 lignes:
    pyv.draw_circle(scr, 'red', (targx, targy), 4)
    pyv.draw_circle(scr, 'red', proj_function(av_i+1, av_j), 4)
    pyv.draw_circle(scr, 'red', proj_function(av_i, av_j+1), 4)
    pyv.draw_circle(scr, 'red', proj_function(av_i+1, av_j+1), 4)

    # TODO réparation old feature : afficher les mobs
    # ----- enemies
    # for enemy_info in self.mod.enemies_pos2type.items():
    #     pos, t = enemy_info
    #     if not self.mod.visibility_m.get_val(*pos):
    #         continue
    #     en_i, en_j = pos[0] * self.CELL_SIDE, pos[1] * self.CELL_SIDE
    #     scr.blit(self.monster_img, (en_i, en_j, 32, 32))
