from . import glvars

pyv = glvars.katasdk.pyved_engine

GameStates = pyv.e_struct.enum(
    'TitleScreen',  # first in the list => initial gamestate
    'Credits',
    'Puzzle',
    'TaxPayment'
)
