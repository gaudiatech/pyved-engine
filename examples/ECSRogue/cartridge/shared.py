screen = None
# (Size of break-out blocks)
BLOCK_SIZE= 40
VISION_RANGE = 4
fov_computer = None


game_state = {
            "rm": None,
            "player_pos": None,
            "visibility_m": None,
            "enemies_pos2type": dict(),
            "equipped_spell": None,
            "owned_spells": set()
        }


CELL_SIDE = 32  # px
WALL_COLOR = (8, 8, 24)
HIDDEN_CELL_COLOR = (24, 24, 24)
