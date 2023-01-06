import katagames_engine as kengin


GameStates = kengin.struct.enum(
    'TitleScreen',
    'Overworld',
    'TownLevel',
    'ForestLevel'
)


# always try to keep your event number low: model->view or model->ctrl comms only
MyEvTypes = kengin.game_events_enum((
    'SelectMenuOption',  # contains option (type: int)

    'LevelChange',  # can trigger a cool transition effect
    'NewDialog',  # open small window for a dialog

    'PlayerMoves'  # new pos that is a target cell | #event attribute(s)=1: targ_pos (type:2-tuple)
))
