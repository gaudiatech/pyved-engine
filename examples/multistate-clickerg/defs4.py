
import katagames_sdk.engine as kataen


# - in this game wrapper, the line below should be the only
# app-specific line
#import gamecrm.test_modular as mygame
#import coremon_main.engine as coremon

# gamestates
GameStates = kataen.enum_builder(
    'MenuScreen',
    'ClickChallg'
)
# artificial import for web context..


# custom events
MyEvTypes = kataen.enum_for_custom_event_types(
    'ChallengeStarts',
)
