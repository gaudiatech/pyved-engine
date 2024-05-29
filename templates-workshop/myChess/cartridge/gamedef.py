"""
Project: Python Chess
(c) All rights reserved | Code LICENCE = GNU GPL

This is a joint work, authors are:
    -Steve Osborne (the very first prototype, encoding game rules)
    [contact: srosborne_at_gmail.com]

    - moonbak (port to python3+pyv, various improvements)
    [contact: thomas.iw@kata.games]
"""

from . import pimodules

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

pyg = pyv.pygame


from .chessintro import ChessintroState
from .chessmatch import ChessmatchState
from . import chdefs


@pyv.Singleton
class SharedStorage:
    def __init__(self):
        self.ev_manager = pyv.get_ev_manager()
        self.ev_manager.setup(chdefs.ChessEvents)
        self.screen = pyv.get_surface()


@pyv.declare_begin
def beginchess(vmst=None):
    pyv.init()
    glvars = SharedStorage.instance()

    # override surfvalues to fix most of images, bc we need a different size...
    sq_size_pixels = (100, 100)
    for iname, sv in pyv.vars.images.items():
        if iname[-6:] == 'square':
            pass
        else:
            pyv.vars.images[iname] = pyg.transform.scale(sv, sq_size_pixels)

    pyv.declare_game_states(
        chdefs.ChessGstates, {
            # do this to bind state_id to the ad-hoc class!
            chdefs.ChessGstates.Chessintro: ChessintroState,
            chdefs.ChessGstates.Chessmatch: ChessmatchState
        }
    )
    glvars.ev_manager.post(pyv.EngineEvTypes.Gamestart)


@pyv.declare_update
def updatechess(info_t):
    glvars = SharedStorage.instance()

    glvars.ev_manager.post(pyv.EngineEvTypes.Update, curr_t=info_t)
    glvars.ev_manager.post(pyv.EngineEvTypes.Paint, screen=glvars.screen)

    glvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def endchess(vmst=None):
    pyv.close_game()
