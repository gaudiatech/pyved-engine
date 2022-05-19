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

# uncommenting these lines is handy...
# In case you're running the template with no local installation of kengi
# import sys
# sys.path.append("..")


import katagames_engine as kengi
kengi.bootstrap_e()


from app_click_challg import ClickChallgState
from app_menu_screen import MenuScreenState
from myrpg_defs import GameStates


# launch the game!
if __name__ == '__main__':
    kengi.init('hd')

    # this line also changes the type of game controller used
    kengi.core.declare_states({
        GameStates.TitleScreen: MenuScreenState,
        GameStates.Overworld: ClickChallgState
    })

    t = kengi.core.get_game_ctrl()
    t.turn_on()
    t.loop()

    kengi.quit()
