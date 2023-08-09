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
pyg = pyv.pygame
epaint = pyv.EngineEvTypes.Paint
eupdate = pyv.EngineEvTypes.Update


@pyv.Singleton
class SharedStorage:
    def __init__(self):
        self.ev_manager = pyv.get_ev_manager()
        self.ev_manager.setup(chdefs.ChessEvents)
        self.screen = pyv.get_surface()


@pyv.declare_begin
def beginchess():
    pyv.init()
    glvars = SharedStorage.instance()

    # let's preload game assets...
    pyv.preload_assets({
        'images': [
            'black_pawn.png',
            'black_rook.png',
            'black_knight.png',
            'black_bishop.png',
            'black_king.png',
            'black_queen.png',

            'white_pawn.png',
            'white_rook.png',
            'white_knight.png',
            'white_bishop.png',
            'white_king.png',
            'white_queen.png',
            
            'white_square.png',
            'brown_square.png',
            'cyan_square.png'
        ],
    }, prefix_asset_folder='images/')
    # override surfvalues to fix most of images, bc we need a different size...
    sq_size_pixels = (100, 100)
    for iname, sv in pyv.vars.images.items():
        if iname[-6:] == 'square':
            pass
        else:
            # print('resized', iname)
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
    glvars.ev_manager.post(eupdate, curr_t=info_t)
    glvars.ev_manager.post(epaint, screen=glvars.screen)
    glvars.ev_manager.update()


@pyv.declare_end
def endchess():
    pyv.close_game()


if __name__ == '__main__':
    pyv.run_game()
