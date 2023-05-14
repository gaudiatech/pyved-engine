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
import pyved_engine as kengi
from chdefs import ChessGstates
from chessintro import ChessintroState
from chessmatch import ChessmatchState


class DummyCls(kengi.GameTpl):
    def init_video(self):
        kengi.init(1)

    def setup_ev_manager(self):
        self._manager.setup(chdefs.ChessEvents)

    def enter(self, vms=None):
        super().enter()

        kengi.declare_game_states(
            ChessGstates,  # Warning it will start with the state in this
            {
                ChessGstates.Chessintro: ChessintroState,
                # bind state_id to class is done automatically by kengi (part 1 /2)
                ChessGstates.Chessmatch: ChessmatchState
            },
            self
        )


chdefs.ref_game_obj = game_obj = DummyCls()
game_obj.loop()
