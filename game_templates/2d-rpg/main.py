"""
2D-RPG Template
---------------
Showcasing very basic features for a rpg:
 - loot, and an inventory system
 - evolving stats, used during combat
 - the ability to kill mobs (monsters, enemies)
 - when you try to kill monsters that are too strong you die
Technical stuff:
 - multi-state game with a menu screen
"""
import katagames_engine as kengi
kengi.bootstrap_e()

from app_forest import ForestState
from app_menu_screen import MenuScreenState
from app_overworld import OverworldState
from myrpg_defs import GameStates


# launch the game!
if __name__ == '__main__':
    kengi.init()

    kengi.declare_states(  # changes the game controller used behind the scene
        GameStates,
        {
            GameStates.TitleScreen: MenuScreenState,
            GameStates.Overworld: OverworldState,
            GameStates.ForestLevel: ForestState
        }
    )
    t = kengi.get_game_ctrl()
    t.turn_on()
    t.loop()

    kengi.quit()
