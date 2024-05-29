"""
Define game modes & custom events
"""
from . import pimodules
pyv = pimodules.pyved_engine


ChessGstates = pyv.struct.enum(
    'Chessintro',
    'Chessmatch',
)

ChessEvents = pyv.game_events_enum((
    'MatchBegins',
    'MoveChosen',  # contains: player_color, from_square, to_square, rook_type, ep_flag
    'Checkmate',  # contains: winner_color
    'Check',
    'CancelMove',  # when playing vs an AI this would cancel 1-2 moves, when PvP this cancels only 1 move
    'PromotionPopup'  # contains: target_square, plcolor [allows the player to select the piece he wants the most!]
))

pltype1 = None
pltype2 = None

# constants
OMEGA_PL_TYPES = ('human', 'randomAI', 'defenseAI', 'offenseAI')
BOARD_POS = (64, 175)  # x, y
