import katagames_engine as kengi
from pokerdefs import MyEvTypes
from tabletop import StdCard, PokerHand


kengi.bootstrap_e()

# - aliases
ReceiverObj = kengi.event.EventReceiver
EngineEvTypes = kengi.event.EngineEvTypes
pygame = kengi.pygame

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

    'bet': (955, 774),
    'blind': (1061, 778),

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

# - glvars
alea_xx = lambda_hand = epic_hand = list()


# --------------
#  game components
# --------------
class UthModel(kengi.event.CogObj):
    """
    Uth: Ultimate Texas Holdem

    STAGES ARE

    0: "eden state" -> cards not dealt, no money spent
    1: cards dealt yes, both ante and blind have been paid, you pick one option: check/bet 3x/ bet 4x
      if bet 4x you go straight to the last state
      if check you go to state 2
    2: flop revealed, your pick one option: check/bet 2x
      if bet 2x you go to the last state
      if check you go to state 3
    3: turn & river revealed you pick one option: fold/ bet 1x
      if bet you go to the final state
      if fold you loose everything except whats in bonus state 5
    4(final):
      all remaining cards are returned, if any then player is paid. Current round halts
    5:
      pay bonus only, current round halts
    """
    def __init__(self):
        super().__init__()
        self.cash = 200  # usd
        self.stage = 0
        self.revealed = {
            'dealer1': False,
            'dealer2': False,
            'flop3': False,
            'flop2': False,
            'flop1': False,
            'turn': False,
            'river': False,
            'player1': False,
            'player2': False
        }
        self.ante = self.blind = 0

    def deal_cards(self, ante_val):
        if self.stage:
            raise ValueError('calling deal_cards while stage !=0')
        else:
            self.revealed['player2'] = self.revealed['player1'] = True
            self.ante = self.blind = ante_val
            self.cash -= 2 * ante_val
            self.stage = 1
            self.pev(MyEvTypes.CardsReveal)
            self.pev(MyEvTypes.CashChanges, value=self.cash)

    def is_player_broke(self):
        return self.cash <= 0


class UthControl(ReceiverObj):
    def __init__(self, model):
        super().__init__()
        self._mod = model

    def proc_event(self, ev, source):
        global alea_xx
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.GAMEENDS)
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            # alea_xx = PokerHand([StdCard.draw_card() for _ in range(5)])  # not from a deck -> raw 1/52 chance
            # TODO blit the type of hand (Two pair, Full house etc) + the score val.
            if self._mod.stage == 0:
                self._mod.deal_cards(6)  # bet 6


class UthView(ReceiverObj):
    def __init__(self, model):
        super().__init__()
        self._assets_rdy = False

        self.bg = None
        self.card_back_img = None

        self.card_images = dict()
        self.chip_spr = dict()

        self._mod = model
        self.ft = pygame.font.Font(None, 72)

        # draw cash amount
        self.cash_etq = self.ft.render(str(self._mod.cash)+'$ ', True, (0, 0, 28), (133, 133, 133))

    def _load_assets(self):
        self._assets_rdy = True

        self.bg = pygame.image.load(BACKGROUND_IMG_PATH)
        self.card_back_img = pygame.image.load('img/back.png').convert_alpha()
        self.card_back_img = pygame.transform.scale(self.card_back_img, CARD_SIZE_PX)

        for card_cod in StdCard.all_card_codes():
            y = PokerHand.adhoc_mapping(card_cod[0]).lstrip('0') + card_cod[1].upper()  # convert card code to path
            img_path = f'img/{y}.png'
            tempimg = pygame.image.load(img_path).convert_alpha()
            self.card_images[card_cod] = pygame.transform.scale(tempimg, CARD_SIZE_PX)

        for chip_val_info in ('2a', '2b', '5', '10', '20'):
            org = chip_val_info
            if chip_val_info == '2a' or chip_val_info == '2b':
                chip_val_info = '2'
            img_path = f'img/chip{chip_val_info}.png'
            tempimg = pygame.image.load(img_path).convert_alpha()
            tempimg = pygame.transform.scale(tempimg, CHIP_SIZE_PX)
            tempimg.set_colorkey((255, 0, 255))
            spr = pygame.sprite.Sprite()
            spr.image = tempimg
            spr.rect = spr.image.get_rect()
            spr.rect.center = PLAYER_CHIPS[org]
            self.chip_spr[chip_val_info] = spr

    def proc_event(self, ev, source):
        global alea_xx, lambda_hand, epic_hand
        if ev.type == EngineEvTypes.PAINT:
            if not self._assets_rdy:
                self._load_assets()
            self._paint(ev.screen)
        elif ev.type == MyEvTypes.CashChanges:
            # RE-draw cash value
            self.cash_etq = self.ft.render(str(ev.value) + '$ ', True, (0, 0, 28), (133, 133, 133))

    @staticmethod
    def centerblit(refscr, surf, p):
        w, h = surf.get_size()
        refscr.blit(surf, (p[0]-w//2, p[1]-h//2))

    def _paint(self, scr):
        scr.blit(self.bg, (0, 0))

        if self._mod.stage == 0:
            # draw cards location
            where_to_draw = (
                'dealer1', 'dealer2', 'player1', 'player2'
            )
            for loc in where_to_draw:
                UthView.centerblit(scr, self.card_back_img, CARD_SLOTS_POS[loc])

        for i in range(5):
            scr.blit(self.card_images[alea_xx[i].code], (25 + 110 * i, 10))
        for i in range(5):
            scr.blit(self.card_images[lambda_hand[i].code], (25 + 110 * i, 158))
        for i in range(5):
            scr.blit(self.card_images[epic_hand[i].code], (25 + 110 * i, 296))
        for k, v in enumerate((2, 5, 10, 20)):
            adhoc_spr = self.chip_spr[str(v)]
            if v == 2:
                adhoc_spr.rect.center = PLAYER_CHIPS['2b']
            scr.blit(adhoc_spr.image, adhoc_spr.rect.topleft)
        self.chip_spr['2'].rect.center = PLAYER_CHIPS['2a']
        scr.blit(self.chip_spr['2'].image, self.chip_spr['2'].rect.topleft)

        scr.blit(self.cash_etq, POS_CASH)

        kengi.flip()


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
