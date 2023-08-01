"""
define game modes & custom events in this file
"""
import pyved_engine as pyv


ChessGstates = pyv.struct.enum(
    'Chessintro',
    'Chessmatch',
)

ChessEvents = pyv.game_events_enum((
    'MoveChosen',  # contains: from_cell, to_cell
))

pltype1 = None
pltype2 = None
OMEGA_PL_TYPES = ('human', 'randomAI', 'defenseAI', 'offenseAI')
