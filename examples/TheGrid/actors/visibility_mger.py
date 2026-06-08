from .. import glvars
from ..glvars import pyv


def new_visibility_mger(ref_maze):
    """
    visibility manager. Dynamically updates what is visible, when
    """
    data = {
        'ref_maze': ref_maze,
        'fov_computer': None,
        'ptr_li_mobs': None,
        'ptr_li_pots': None,
        'ptr_exit_entity': None,
        'map': pyv.struct.BoolMatrix((glvars.MAP_W, glvars.MAP_H))
    }

    # -----------
    #  utils
    def test(this, cell):  # test if one can see the given cell
        if glvars.GODMODE:
            return True
        return this.map.get_val(*cell)

    def refresh_player_pov(this, pl_pos):
        if this.fov_computer is None:
            this.fov_computer = pyv.rogue.FOVCalc()

        i, j = pl_pos
        this.map.set_val(i, j, True)  # av_pos always visible!

        def func_visibility(a, b):
            if this.map.is_out(a, b):
                return False
            if pyv.trigger('get_cell_terrain', glvars.ref_maze, a, b) is None:  # cannot see through walls
                return False
            return True

        li_visible = this.fov_computer.calc_visible_cells_from(i, j, glvars.VISION_RANGE, func_visibility)
        for cell in li_visible:
            this.map.set_val(cell[0], cell[1], True)

    # -----------
    #  behavior
    def on_maze_generated(this, ev):
        this.map.set_all(False)
        # copy references
        this.ptr_li_mobs = ev.li_mobs
        this.ptr_li_pots = ev.li_pots
        this.ptr_exit_entity = ev.exit_entity
        # entities:
        for m in ev.li_mobs:
            pyv.peek(m).visible = True
        for p in ev.li_pots:
            pyv.peek(p).visible = True
        pyv.peek(ev.exit_entity).visible = True
        # bc the player just spawned, and hasnt moved, we need to force refresh
        pl_pos = pyv.peek(ev.ref_player).pos
        refresh_player_pov(this, pl_pos)

    def on_player_movement(this, ev):
        refresh_player_pov(this, ev.pos)

    return pyv.new_actor('visibility_mger', locals())
