#import katagames_sdk as katasdk
import pyved_engine as pyv
#katasdk.bootstrap()
#kengi = katasdk.kengi
kengi= pyv

refgame, refmodel, refview = None, None, None


def chip_scrolldown(x):
    global refmodel
    omega = (2, 5, 10, 20)
    curridx = omega.index(x)
    curridx -= 1
    if curridx < 0:
        curridx = len(omega) - 1
    y = omega[curridx]
    refmodel.set_chipvalue(y)


def chip_scrollup(x):
    global refmodel
    omega = (2, 5, 10, 20)
    curridx = omega.index(x)
    curridx = (curridx + 1) % len(omega)
    y = omega[curridx]
    refmodel.set_chipvalue(y)


PokerStates = kengi.struct.enum(
    'AnteSelection',
    'PreFlop',
    'Flop',
    'TurnRiver',
    'Outcome'
)

MyEvTypes = kengi.game_events_enum((
    'StackChip',  # used to bet in an incremental way, contains: trips(True/False)
    'CycleChipval',  # contains: upwards(int: 1 or 0), to answer 'do we cycle 2->5->10->... or the other way around?'

    # - IMPACT from buttons in AnteSelectionState
    'DealCards',  # this litteraly means ->clicking the Start button... In AnteSelection stage
    'BetIdem',
    'BetUndo',
    'BetReset',

    # - IMPACT from buttons (generic)
    'BetDecision',
    'BetHighDecision',  # can be sent only from the PreFlopState
    'CheckDecision',  # can also represent a FOLD operation (at the TurnRiverState)

    'NewMatch',
    'MoneyUpdate',  # contains: ante, bet, play, trips, wealth
    'ChipUpdate',  # contains: value
    'StateChanges',  # contains: pokerstate
    'RienNeVaPlus',  # sent when player has chosen bet or fold
    'MatchOver',  # contains: won(-1, 0, +1)
))
