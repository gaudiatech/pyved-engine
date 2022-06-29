import katagames_engine as kengi
kengi.bootstrap_e()

from uth_model import UthModel, StdCard, PokerHand
from uth_ux import UthView, UthControl


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
        card = StdCard.draw_card(deja_pioche)
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
    print('score= ' + str(ma_main.score))

    print('-- fin tests base modele --')
    print()


def run_game():
    global alea_xx, lambda_hand, epic_hand
    _init_and_tests()

    # ---- extra tests on model ----
    print('ex. de scores:')
    alea_xx = PokerHand([
        StdCard('2h'), StdCard('5s'), StdCard('9d'), StdCard('Kd'), StdCard('Tc')
    ])
    print('   _', alea_xx.score)

    lambda_hand = PokerHand([
        StdCard('Ah'), StdCard('Jc'), StdCard('Ts'), StdCard('5s'), StdCard('3d')
    ])
    print('   _', lambda_hand.score)
    # - royal flush
    epic_hand = PokerHand([
        StdCard('Ad'), StdCard('Qd'), StdCard('Kd'), StdCard('Td'), StdCard('Jd')
    ])
    print('   _', epic_hand.score)

    # ------- init kengi ------
    kengi.init('custom', screen_dim=(1920, 1080))

    # >>> the game loop
    mod = UthModel()
    receivers = [
        UthView(mod),
        UthControl(mod),
        kengi.get_game_ctrl()
    ]
    for robj in receivers:
        robj.turn_on()
    receivers[-1].loop()
    print('bye!')


if __name__ == '__main__':
    run_game()
