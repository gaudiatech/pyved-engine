screen = None
end_game_label = None
# (Size of break-out blocks)
BLOCK_SIZE= 40
VISION_RANGE = 4
fov_computer = None


game_state = {
            "rm": None,
            "visibility_m": None,
            "enemies_pos2type": dict(),
            "equipped_spell": None,
            "owned_spells": set()
        }


CELL_SIDE = 32  # px
WALL_COLOR = (8, 8, 24)
HIDDEN_CELL_COLOR = (24, 24, 24)

# extra const
GRID_REZ = (CELL_SIDE, CELL_SIDE)

AVATAR = None
MONSTER = None
TILESET = None

walkable_cells = []  # List to store walkable cells
old_position = 0

last_hit_key = None
