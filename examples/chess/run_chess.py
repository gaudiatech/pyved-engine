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
from chdefs import ChessGstates
from chessintro import ChessintroState
from chessmatch import ChessmatchState


class DummyCls(kengi.GameTpl):
    def enter(self, vms=None):
        kengi.init(1)
        self._manager = kengi.get_ev_manager()
        self._manager.setup(chdefs.ChessEvents)

        kengi.declare_game_states(
            ChessGstates,  # Warning it will start with the state in this
            {
                ChessGstates.Chessintro: ChessintroState,
                # bind state_id to class is done automatically by kengi (part 1 /2)
                ChessGstates.Chessmatch: ChessmatchState
            }
        )


chdefs.ref_game_obj = game_obj = DummyCls()
game_obj.loop()
