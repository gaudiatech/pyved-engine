"""
here we can define all actors that fall in the 'monsters' category
"""
from .. import glvars
from ..glvars import pyv


Pathfinder = pyv.terrain.DijkstraPathfinder


def new_monster(gpos, mtype):
    # anciennement pr chaque monstre on vait:

    # 'position': position,
    # 'damages': shared.MONSTER_DMG,
    # 'health_point': shared.MONSTER_HP,
    # 'active': False  # the mob will become active, once the player sees it
    data = {
        'pos': tuple(gpos), 'monster_type': mtype, 'active': False
    }

    def kill(this):
        auto_id = pyv.id_actor(this)
        pyv.del_actor(auto_id)
        pyv.post_ev('item_destroyed', id=auto_id)

    def on_player_movement(this, ev):
        if ev.pos == this.pos:  # monster plays after player, so he can get killed 1st
            kill(this)
            print('player slays the enemy!')
            pyv.trigger('change_hp', glvars.ref_player, -10)
            return
        blockmap = pyv.peek(glvars.ref_maze).content.blocking_map

        pathfinding_result = Pathfinder.find_path(
            blockmap, this.pos, ev.pos
        )
        if pathfinding_result:
            if len(pathfinding_result) < 2:
                raise RuntimeError('shouldnt be there?')
            else:
                future_pos = pathfinding_result[1]
            if len(pathfinding_result) == 2:
                # bash player
                pyv.trigger('change_hp', glvars.ref_player, -35)
                print('enemy leaps forward!')
                kill(this)
            else:
                this.pos = tuple(future_pos)  # mob moves

    def on_draw(this, ev):
        mob_position = this.pos
        if not pyv.trigger('test', glvars.ref_visibility_mger, mob_position):
            return  # avoid drawing invisble things
        en_i, en_j = mob_position[0] * glvars.CELL_SIDE, mob_position[1] * glvars.CELL_SIDE
        ev.screen.blit(glvars.monster_img, (en_i, en_j, 32, 32))

    return pyv.new_actor('monster', locals())
