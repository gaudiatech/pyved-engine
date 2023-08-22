
from . import glvars

pyv = glvars.katasdk.pyved_engine

BlokuEvents = pyv.game_events_enum((
    'Validation',

    # - LoginState
    'LoginStUsernameChanges',  # contains txt
    'LoginStPwdChanges',  # contains txt(not a plain pwd str!)
    'LoginStFocusChanges',  # contains focusing_username=True/False
    'TrigValidCredentials',  # no attr
    'PlayerLogsIn',  # sent after succesful auth, contains username:str, solde:int

    # - Puzzle state
    'NewPieces',  # bag has been re-filled, no attr
    'ScoreChanges',  # contient score=int
    'GameLost',
    'LineDestroyed',
    'BlocksCrumble',

    # - TitleScreen state
    'ChoiceChanges',  # contient code
    'BalanceChanges',  # contiendra value (un int)
    'DemandeTournoi',

    # - Taxpayment state
    'LoadingBarMoves',
))
