import katagames_engine as kengi


ChessEvents = kengi.game_events_enum((
    'MoveChosen',  # contains: from_cell, to_cell
))
