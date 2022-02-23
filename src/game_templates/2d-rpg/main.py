"""
2d-rpg template

we define several game states,
and see how the dev can switch from one to another.
"""

import katagames_engine as kengi
from app_click_challg import ClickChallgState
from app_menu_screen import MenuScreenState
from myrpg_defs import GameStates


if __name__ == '__main__':
    kengi.core.init()

    kengi.core.declare_states({
        GameStates.TitleScreen: MenuScreenState,
        GameStates.Overworld: ClickChallgState
    })

    t = kengi.core.get_game_ctrl()
    t.turn_on()
    t.loop()

    kengi.core.cleanup()
