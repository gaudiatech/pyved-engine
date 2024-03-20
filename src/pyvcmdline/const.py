# ---------------------
# constants for the sub command "pub"
# ---------------------

TARG_TRIGGER_PUBLISH = 'https://kata.games/api/uploads.php'  # script to upload the end result (Published game)

POSSIB_TEMPLATES = {
    0: 'Empty',
    1: 'Breakout',
    2: 'Platformer',
    3: 'Chess',
    4: 'Roguelike'
}
MAX_TEMPLATE_ID = 4

VERSION_PRINT_MESSAGE = 'pyved-engine v. %s (c) 2018-2024 the Kata.Games Team, Thomas EDER et al.'
