
import katagames_sdk.engine as kataen
from defs4 import GameStates

from app_click_challg import ClickChallgState
from app_menu_screen import MenuScreenState


def run_game():
    kataen.init(kataen.HD_MODE)
    #mygame.run()
    st_classes = {
        'MenuScreenState': MenuScreenState,
        'ClickChallgState': ClickChallgState
    }
    kataen.tag_multistate(GameStates, kataen.import_pygame(), False, providedst_classes=st_classes)
    t = kataen.get_game_ctrl()
    t.turn_on()
    t.loop()
    
    kataen.cleanup()

if __name__=='__main__':
    run_game()
