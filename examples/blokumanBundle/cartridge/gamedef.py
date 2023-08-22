# import sharedvars
from . import pimodules
from . import glvars as vars

vars.katasdk = pimodules
pyv = pimodules.pyved_engine

pyv.bootstrap_e()

pyg = pyv.pygame
# sharedvars.katasdk
from . import util

util.init_fonts_n_colors()  # need to init colors before loading TitleView, otherwise --> crash!

# from katagames_sdk.capsule.networking.httpserver import HttpServer
from .defs import GameStates
from . import loctexts
from .puzzle_state import PuzzleState
from .menu_state import TitleScreenState
from .ev_types import BlokuEvents
from . import glvars

# TODO: fix
HttpServer = None


# HttpServer = old_v_kengi.network.HttpServer  # katasdk.network.HttpServer in future versions


# class BlokuGame(kengi.GameTpl):
#
#
#         # xxx DOUBLEMENT deprecated xxx
#         ## - juste un test réseau, ce reset game ne sert a rien pour BLOKU-MAN,
#         ## il est utile pour mConquest...
#         ## serv = HttpServer.instance()
#         ## url = 'https://sc.gaudia-tech.com/tom/'
#         ## params = {}
#         ## full_script = url+'resetgame.php'
#         ## print(full_script)
#         ## res = serv.proxied_get(full_script, params)
#         ## game_ctrl = kengi.get_game_ctrl()
#         ## game_ctrl.turn_on()
#
#         important! Its needed to proc the 1st gstate 'do_init' method
#         self._manager.post(kengi.EngineEvTypes.Gamestart)


# blokuwrapper.glvars.gameref = game = BlokuGame()
# katasdk.gkart_activation(game)


# TODO rewrite the game loop/boilerplate
class BlokumanGame(pyv.GameTpl):

    def get_video_mode(self):
        return 1

    def list_game_events(self):
        return BlokuEvents

    def enter(self, vms=None):
        # safer this way:
        self.nxt_game = 'game_selector'
        loctexts.init_repo(glvars.CHOSEN_LANG)
        super().enter(vms)
        pyv.declare_game_states(  # doit etre appelé après le setup_ev_manager !!!
            GameStates,
            {
                GameStates.TitleScreen: TitleScreenState,
                GameStates.Puzzle: PuzzleState
            }
        )


game = BlokumanGame()
