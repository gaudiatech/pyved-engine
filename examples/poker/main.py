import katagames_engine as kengi
kengi.bootstrap_e()

from UthModel import UthModel, StandardCard, PokerHand
from UthView import UthView
from UthCtrl import UthCtrl


# - aliases
ReceiverObj = kengi.event.EventReceiver
EngineEvTypes = kengi.event.EngineEvTypes
pygame = kengi.pygame

# - glvars
alea_xx = lambda_hand = epic_hand = list()


# --------------
#  functions only
# --------------
def _init_and_tests():
    """
    ----------------------------------------------
       W.i.p. <> below I perform some tests legacy classes/
       chunks copied from elsewhere still need to be merged/unified
    -----------------------------------------------
    """
    deja_pioche = set()
    future_main = list()
    for _ in range(5):
        card = StandardCard.at_random(deja_pioche)
        print(card, '|', card.code)
        deja_pioche.add(card.code)
        future_main.append(card)

    ma_main = PokerHand(future_main)
    print(ma_main)
    print('-- fin tests affichage --')
    print()

    # TODO implem fct. manquante
    print('flush? ', ma_main.is_flush())
    print('straight? ', ma_main.is_straight())
    print('score= ' + str(ma_main.value))

    print('-- fin tests base modele --')
    print()


def run_game():
    global alea_xx, lambda_hand, epic_hand
    _init_and_tests()

    # ---- extra tests on model ----
    print('ex. de scores:')
    alea_xx = PokerHand([
        StandardCard('2h'), StandardCard('5s'), StandardCard('9d'), StandardCard('Kd'), StandardCard('Tc')
    ])
    print('   _', alea_xx.value)

    lambda_hand = PokerHand([
        StandardCard('Ah'), StandardCard('Jc'), StandardCard('Ts'), StandardCard('5s'), StandardCard('3d')
    ])
    print('   _', lambda_hand.value)
    # - royal flush
    epic_hand = PokerHand([
        StandardCard('Ad'), StandardCard('Qd'), StandardCard('Kd'), StandardCard('Td'), StandardCard('Jd')
    ])
    print('   _', epic_hand.value)

    # ------- init kengi ------
    kengi.init(0, screen_dim=(1920, 1080))

    # >>> the game loop
    mod = UthModel()
    receivers = [
        UthView(mod),
        UthCtrl(mod),
        kengi.get_game_ctrl()
    ]
    for robj in receivers:
        robj.turn_on()
    receivers[-1].loop()
    print('bye!')


if __name__ == '__main__':
    run_game()
