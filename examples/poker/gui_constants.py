
# - program constants
BACKGROUND_IMG_PATH = 'img/bg0.jpg'
CARD_SIZE_PX = (82, 120)
CHIP_SIZE_PX = (62, 62)
POS_CASH = (1192, 1007)
CARD_SLOTS_POS = {  # coords in pixel so cards/chips & BG image do match; cards img need an anchor at the middle.
    'dealer1': (905, 329),
    'dealer2': (1000, 333),

    'flop3': (980, 470),
    'flop2': (1075, 473),
    'flop1': (1173, 471),

    'turn': (846, 473),
    'river': (744, 471),

    'player1': (1125, 878),
    'player2': (1041, 880),

    'ante': (935, 757),
    'bet': (935, 850),
    'blind': (1040, 757),

    'raise1': (955, 870),
    'raise2': (961, 871),
    'raise3': (967, 872),
    'raise4': (973, 873),
    'raise5': (980, 875),
    'raise6': (986, 876)
}
PLAYER_CHIPS = {
    '2a': (825, 1000),
    '2b': (905, 1000),
    '5': (985, 1000),
    '10': (1065, 1000),
    '20': (1145, 1000)
}
