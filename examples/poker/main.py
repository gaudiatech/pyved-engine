import pyved_engine as pyv

pyv.bootstrap_e()

from mvc_components import UthModel, UthView, UthCtrl
from pokerdefs import MyEvTypes


ReceiverObj = pyv.EvListener
EngineEvTypes = pyv.EngineEvTypes
pygame = pyv.pygame
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
        card = pyv.tabletop.StandardCard.at_random(deja_pioche)
        print(card, '|', card.code)
        deja_pioche.add(card.code)
        future_main.append(card)

    ma_main = pyv.tabletop.PokerHand(future_main)
    print(ma_main)
    print('-- fin tests affichage --')
    print()

    # TODO implem fct. manquante
    print('flush? ', ma_main.is_flush())
    print('straight? ', ma_main.is_straight())
    print('score= ' + str(ma_main.value))

    print('-- fin tests base modele --')
    print()


class MyGameCtrl(pyv.EvListener):
    MAXFPS = 75

    def __init__(self):
        super().__init__()
        self._clock = pygame.time.Clock()
        self.active_gameloop = True

    def on_gameover(self, ev):
        self.active_gameloop = False

    def loop(self):
        while self.active_gameloop:
            self.pev(pyv.EngineEvTypes.Update)
            self.pev(pyv.EngineEvTypes.Paint, screen=pyv.get_surface())
            self._manager.update()
            pyv.flip()
            self._clock.tick(self.MAXFPS)


def run_game():
    global alea_xx, lambda_hand, epic_hand
    _init_and_tests()

    # ---- extra tests on model ----
    # print('ex. de scores:')
    # alea_xx = PokerHand([
    #     StandardCard('2h'), StandardCard('5s'), StandardCard('9d'), StandardCard('Kd'), StandardCard('Tc')
    # ])
    # print('   _', alea_xx.value)
    #
    # lambda_hand = PokerHand([
    #     StandardCard('Ah'), StandardCard('Jc'), StandardCard('Ts'), StandardCard('5s'), StandardCard('3d')
    # ])
    # print('   _', lambda_hand.value)
    # # - royal flush
    # epic_hand = PokerHand([
    #     StandardCard('Ad'), StandardCard('Qd'), StandardCard('Kd'), StandardCard('Td'), StandardCard('Jd')
    # ])
    # print('   _', epic_hand.value)

    # ------- init kengi ------
    pyv.init(0, screen_dim=(1920, 1080))
    pyv.get_ev_manager().setup(MyEvTypes)

    # >>> the game loop
    mod = UthModel()
    receivers = [
        UthView(mod),
        UthCtrl(mod),
        MyGameCtrl()
    ]
    for robj in receivers:
        robj.turn_on()
    receivers[-1].loop()
    print('bye!')


if __name__ == '__main__':
    run_game()
