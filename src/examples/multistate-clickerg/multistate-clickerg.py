"""
Main file for the example!

here we define several game states, and see how the dev can
switch from one to the other.
"""

import katagames_engine as kengi
from app_click_challg import ClickChallgState
from app_menu_screen import MenuScreenState
from defs4 import GameStates
import glvars


if __name__ == '__main__':
    kengi.core.init()

    st_classes = {
        'MenuScreenState': MenuScreenState,
        'ClickChallgState': ClickChallgState
    }
    kengi.legacy.tag_multistate(
        GameStates, glvars, False, providedst_classes=st_classes
    )

    t = kengi.core.get_game_ctrl()
    t.turn_on()
    t.loop()
    kengi.core.cleanup()
