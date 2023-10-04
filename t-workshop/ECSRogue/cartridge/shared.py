screen = None
end_game_label0 = None
end_game_label1 = None

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

SCR_WIDTH = 960
SCR_HEIGHT = 720

# extra const
GRID_REZ = (CELL_SIDE, CELL_SIDE)

AVATAR = None

PLAYER_DMG = 10
PLAYER_HP = 100

MONSTER_DMG = 10
MONSTER_HP = 20
MONSTER = None
TILESET = None

walkable_cells = []  # List to store walkable cells
level_count = 1

