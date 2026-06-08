"""
contains: maze generation,
here we also defin the "maze" actor
"""
from .misc import *
from .monsters import new_monster
from .player import new_player
from .. import glvars
from ..glvars import pyv


def is_visible(cell) -> bool:
    # both syntax work(ex 1):
    # return pyv.peek(glvars.ref_visibility_mger).map.get_val(*cell)
    # (ex 2):
    return pyv.trigger('test', glvars.ref_visibility_mger, cell)


def new_maze():
    """
    contient:
    model = terrain, position des murs, visibilité, cases acessibles, info.vision
    view = affichage sol
    """
    data = {
        'content': None,  # will contain a special item created by pyv
        'visibility_map': None,
        'exit_entity': None,
        'li_mobs': list(),
        'li_pots': list(),
        'ref_player': None,
    }

    # - utility
    def get_cell_terrain(this, a, b):
        y = this.content.getMatrix().get_val(a, b)
        # print(f'get cell terrain({a},{b})-->', y)
        return y

    def add_monster(this, gpos, mtype):
        this.table.append({
            'pos': gpos,
            'monster_type': mtype,
            'seen': False,
            'active': False
        })

    # def list_walkable_cells():  # static
    #     walkable_cells = list()
    #     for i in range(glvars.MAP_W):
    #         for j in range(glvars.MAP_H):
    #             walkable_cells.append((i, j))
    #     return walkable_cells

    def terrain_gen(this):
        # reset old map, if some data existed
        if this.exit_entity:
            pyv.del_actor(this.exit_entity)
            this.exit_entity = None
        if this.ref_player:
            pyv.del_actor(this.ref_player)
            this.ref_player = None
            glvars.ref_player = None

        # pl_ent = pyv.find_by_archetype('player')[0]
        # monsters = pyv.find_by_archetype('monster')
        # potion = pyv.find_by_archetype('potion')[0]
        # exit_ent = pyv.find_by_archetype('exit')[0]

        # why so?
        # if pl_ent['enter_new_map']:
        #    pl_ent['enter_new_map'] = False
        #    print('Level generation...')

        this.content = pyv.rogue.RandomMaze(glvars.MAP_W, glvars.MAP_H, min_room_size=3, max_room_size=5)
        # print(shared.game_state['rm'].blocking_map)

        # IMPORTANT:
        # adding exit & player & mobs comes before computing the visibility
        # >>> player
        pos_pl_spawn = this.content.pick_walkable_cell()
        # --- spawn player
        # TODO tp the player ??
        # pyv.find_by_archetype('player')[0]['position'] =
        # world.update_vision_and_mobs(
        #     pyv.find_by_archetype('player')[0]['position'][0],
        #     pyv.find_by_archetype('player')[0]['position'][1]
        # )
        # request_player_spawn(this, pos_pl_spawn)
        this.ref_player = new_player(pos_pl_spawn)
        glvars.ref_player = this.ref_player
        # update_vision(this)

        # >>> extra entity:
        # the level exit
        forbidden_loc = [
            pos_pl_spawn,
            # what about monsters??
        ]
        while True:
            exit_test_pos = this.content.pick_walkable_cell()
            if exit_test_pos not in forbidden_loc:
                this.exit_pos = exit_test_pos
                this.exit_entity = new_exit_entity(exit_test_pos)
                print('exit created @', this.exit_pos)
                break

        # >>> extra entities :
        #  mobs:
        # first, flush the list of mobs
        for e in this.li_mobs:
            pyv.del_actor(e)
        del this.li_mobs[:]
        # shared.game_state["enemies_pos2type"].clear()
        for _ in range(5):
            tmp = this.content.pick_walkable_cell()
            # do i need to call .add_monster instead?
            # pyv.actor_exec(glvars.ref_monsters, 'add_monster', pos_key, 1)
            # print('nouv monster-->', tmp)
            this.li_mobs.append(new_monster(tmp, 1))

        #  extra entity : POTS!
        for e in this.li_pots:
            pyv.del_actor(e)
        del this.li_pots[:]
        for _ in range(glvars.NB_POTS_PER_MAP):
            ppos = this.content.pick_walkable_cell()
            this.li_pots.append(new_potion(ppos))

        # ???
        # while True:
        #     resultat = random.randint(0, 1)
        #     potionPos = shared.random_maze.pick_walkable_cell()
        #     if potionPos not in [pl_ent.position] + [monster.position for monster in monsters] + [
        #         exit_ent.position]:
        #         potion.position = potionPos
        #         if resultat == 0:
        #             potion.effect = 'Heal'
        #         else:
        #             potion.effect = 'Poison'
        #         break

        # where can i walk:
        del glvars.walkable_cells[:]
        for i in range(glvars.MAP_W):
            for j in range(glvars.MAP_H):
                # all but not walls
                if get_cell_terrain(this, i, j) is not None:
                    glvars.walkable_cells.append((i, j))
        pyv.post_ev(
            'maze_generated',
            li_mobs=this.li_mobs, li_pots=this.li_pots, exit_entity=this.exit_entity, ref_player=this.ref_player
        )

    # - behavior
    def on_item_destroyed(this, ev):
        if ev.id in this.li_pots:
            this.li_pots.remove(ev.id)
        if ev.id in this.li_mobs:
            this.li_mobs.remove(ev.id)
        print('entities left on map:', 1+len(this.li_mobs)+len(this.li_pots))

    # def on_enemies_turn(this, ev):
    #     print('ds maze')
    #     pl_pos = pyv.peek(glvars.ref_player).pos
    #     to_kill = set()
    #     for e in this.li_enemies:
    #         hits = pyv.trigger('do_walk', e)
    #         if hits:
    #             to_kill.add(e)
    #             pyv.actor_exec(glvars.ref_player, 'gets_hit')
    #
    #     pyv.trigger('commit_move', glvars.ref_player)  # pl pos changed
    #     if len(this.li_potions) > 0:
    #         pot_ref = this.li_potions[0]
    #         pot_loc = pyv.actor_state(pot_ref).pos
    #         pl_loc = pyv.actor_state(glvars.ref_player).pos
    #         print(f'pl_loc {pl_loc} / pot_loc {pot_loc}')
    #         if  pl_loc == pot_loc:
    #             # pl just walked over the pot
    #             print('signal drink!')
    #             this.li_potions.remove(pot_ref)
    #             pyv.post_ev('drink')

    def on_req_refresh_maze(this, ev):
        # happens when player finds staircase and use it
        terrain_gen(this)

    def on_game_restart(this, ev):
        glvars.level_count = 1
        glvars.avatar_hp = 100
        glvars.game_paused = False
        terrain_gen(this)

    def on_draw(this, ev):
        scr = ev.screen
        scr.fill(glvars.WALL_COLOR)
        # ----------
        #  draw tiles
        # ----------
        nw_corner = (0, 0)
        tmp_r4 = [None, None, None, None]
        # si tu veux afficher du sol, vraiment du sol
        # tuile = shared.TILESET.image_by_rank(912)
        dim = glvars.MAP_W, glvars.MAP_H  #get_terrain().get_size()
        for i in range(dim[0]):
            for j in range(dim[1]):
                # TODO a way to cache non-walls tiles, for a better perf?
                # ignoring walls
                cell_content = get_cell_terrain(this, i, j)
                if cell_content is None:
                    continue
                tmp_r4[0], tmp_r4[1] = nw_corner
                tmp_r4[0] += i * glvars.CELL_SIDE
                tmp_r4[1] += j * glvars.CELL_SIDE
                tmp_r4[2] = tmp_r4[3] = glvars.CELL_SIDE
                if not is_visible((i, j)):  # hidden cell
                    pyv.draw_rect(scr, glvars.HIDDEN_CELL_COLOR, tmp_r4)
                else:
                    # texture:
                    # scr.blit(tuile, tmp_r4)
                    pyv.draw_rect(scr, glvars.CELL_COLOR, tmp_r4)

    return pyv.new_actor('maze', locals())
