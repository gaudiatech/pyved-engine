"""
Project: Python Chess
(c) All rights reserved | Code LICENCE = GNU GPL

This is a joint work, authors are:
    -Steve Osborne (the very first prototype, encoding game rules)
    [contact: srosborne_at_gmail.com]

    -Thomas Iwaszko (port to python3+pyv, various improvements)
    [contact: thomas.iw@kata.games]
"""

import chdefs
import pyved_engine as pyv
from chessintro import ChessintroState
from chessmatch import ChessmatchState


# aliases
epaint = pyv.EngineEvTypes.Paint
eupdate = pyv.EngineEvTypes.Update

# gl. vars
ev_manager = scr = None


@pyv.declare_begin
def beginchess():
    global ev_manager, scr
    pyv.init()
    ev_manager = pyv.get_ev_manager()
    ev_manager.setup(chdefs.ChessEvents)
    scr = pyv.get_surface()
    pyv.declare_game_states(
        chdefs.ChessGstates, {
            # do this to bind state_id to the ad-hoc class!
            chdefs.ChessGstates.Chessintro: ChessintroState,
            chdefs.ChessGstates.Chessmatch: ChessmatchState
        },
        None
    )
    ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
def updatechess(info_t):
    ev_manager.post(eupdate, curr_t=info_t)
    ev_manager.post(epaint, screen=scr)
    ev_manager.update()


@pyv.declare_end
def endchess():
    pyv.close_game()


if __name__ == '__main__':
    pyv.run_game()
