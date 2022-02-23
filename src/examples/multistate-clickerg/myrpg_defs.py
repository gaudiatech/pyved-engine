
import katagames_engine as kengin


# - in this game wrapper, the line below should be the only
# app-specific line
#import gamecrm.test_modular as mygame
#import coremon_main.engine as coremon

# gamestates
GameStates = kengin.struct.enum_builder(
    'MenuScreen',
    'ClickChallg'
)
# artificial import for web context..


# custom events
MyEvTypes = kengin.event.enum_custom_ev_types(
    'ChallengeStarts',
)
