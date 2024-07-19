
from cartridge import pimodules
from launch_game import Injector
pimodules.upward_link = mon_inj = Injector(None)
mon_inj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')

from cartridge.chess_rules import ChessRules
from cartridge.ChessBoard import ChessBoard


# ---------------------------
#  debug
# ---------------------------
if __name__ == '__main__':

    btest = ChessBoard()
    print('los predicate:', ChessRules.clear_los_predicate(btest, (1, 3), (4, 6)))
