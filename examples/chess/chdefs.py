"""
Define game modes & custom events
"""
import pyved_engine as pyv


ChessGstates = pyv.struct.enum(
    'Chessintro',
    'Chessmatch',
)

ChessEvents = pyv.game_events_enum((
    'MatchBegins',
    'MoveChosen',  # contains: player_color, from_square, to_square, rook_type, ep_flag
    'Checkmate',  # contains: winner_color
    'CancelMove',  # when playing vs an AI this would cancel 1-2 moves, when PvP this cancels only 1 move
    'PromotionPopup'  # allows the human player to select the piece he wants the most!
))

pltype1 = None
pltype2 = None
OMEGA_PL_TYPES = ('human', 'randomAI', 'defenseAI', 'offenseAI')
