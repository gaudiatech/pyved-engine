"""
define game modes & custom events in this file
"""
import katagames_engine as kengi


ChessGstates = kengi.struct.enum(
    'Chessintro',
    'Chessmatch',
)

ChessEvents = kengi.game_events_enum((
    'MoveChosen',  # contains: from_cell, to_cell
))


ref_game_obj = None
