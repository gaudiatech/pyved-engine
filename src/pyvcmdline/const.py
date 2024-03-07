# ---------------------
# constants for the sub command "pub"
# ---------------------

TARG_TRIGGER_PUBLISH = 'https://kata.games/api/uploads.php'  # script to upload the end result (Published game)

# - just various constants
PLAY_SCRIPT_NAME = 'launch_game'
POSSIB_TEMPLATES = {
    0: 'Empty',
    1: 'Breakout',
    2: 'Platformer',
    3: 'Chess',
    4: 'Roguelike'
}
MAX_TEMPLATE_ID = 4
VERSION_PRINT_MESSAGE = 'Pyved-engine version %s (c) 2018-2023 the Kata.Games Team: Thomas Iwaszko and contributors.'
VALID_SUBCOMMANDS = (
    'init',
    'test',
    'play',
    'share',
    'pub'
)
