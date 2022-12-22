"""
Project - Python Chess
(c) All rights reserved | Code LICENCE = GNU GPL

This is a joint work. Authors are:

- Steve Osborne (the very first prototype, encoding game rules)
   [contact: srosborne_at_gmail.com]

- Thomas Iwaszko (port to python3+kengi, game improvement)
   [contact: tom@kata.games]
"""
import chdefs
import katagames_engine as kengi

kengi.bootstrap_e()


from chdefs import ChessGstates
from chessintro import ChessintroMode
from chessmatch import ChessmatchMode


# - aliases
pygame = kengi.pygame

AIvsAI = False
AIpause = False
AIpauseSeconds = 0.0
endgame_msg_added = False


# parser = OptionParser()
# parser.add_option(
#     "-d", dest="debug",
#     action="store_true", default=False, help="Enable debug mode (different starting board configuration)"
# )
# parser.add_option(
#     "-t", dest="text",
#     action="store_true", default=False, help="Use text-based GUI"
# )
# parser.add_option(
#     "-o", dest="old",
#     action="store_true", default=False, help="Use old graphics in pygame GUI"
# )
# parser.add_option(
#     "-p", dest="pauseSeconds", metavar="SECONDS",
#     action="store", default=0, help="Sets time to pause between moves in AI vs. AI games (default = 0)"
# )
# (giv_options, args) = parser.parse_args()


class DummyCls(kengi.GameTpl):
    def enter(self, vms=None):
        kengi.init(1)
        self._manager = kengi.get_ev_manager()
        self._manager.setup(chdefs.ChessEvents)

        kengi.declare_game_states(
            ChessGstates,  # Warning it will start with the state in this
            {
                ChessGstates.Chessintro: ChessintroMode,
                # bind state_id to class is done automatically by kengi (part 1 /2)
                ChessGstates.Chessmatch: ChessmatchMode
            }
        )


chdefs.ref_game_obj = game_obj = DummyCls()
game_obj.loop()
