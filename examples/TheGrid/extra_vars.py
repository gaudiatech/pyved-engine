"""
using a different file (not glvars.py) may be a good idea if you need to initialize variables first,
and need to use the game engine to do so
"""
from .glvars import pyv




screen = None
end_game_label0 = None
end_game_label1 = None

# (Size of break-out blocks)

fov_computer = None


random_maze = None
game_state = {
            "visibility_m": None,
            "enemies_pos2type": dict(),
            "equipped_spell": None,
            "owned_spells": set()
        }


MONSTER = None
TILESET = None
