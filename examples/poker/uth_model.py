import katagames_engine as kengi
from pokerdefs import MyEvTypes
from tabletop import StdCard, PokerHand
print(PokerHand)


class UthModel(kengi.event.CogObj):
    INIT_ST_CODE, DISCOV_ST_CODE, FLOP_ST_CODE, TR_ST_CODE, OUTCOME_ST_CODE = range(1, 5+1)

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

        # stored lists of cards
        self.dealer_hand = []
        self.player_hand = []
        self.flop_cards = []
        self.turnriver_cards = []

        self._stage = None
        self.set_stage(self.INIT_ST_CODE)

    # --- this allows for easier debugging ---
    def set_stage(self, sid):
        assert 1 <= sid <= 5
        self._stage = sid
        print(f' --new state-- >>> {sid}')

    # avoid external modification of stage => encapsulate data
    @property
    def stage(self):
        return self._stage

    def deal_cards(self, ante_val):
        if self.stage != UthModel.INIT_ST_CODE:
            raise ValueError('calling deal_cards while model isnt in the initial state')

        self.revealed['player2'] = self.revealed['player1'] = True

        self.ante = self.blind = ante_val
        self.cash -= 2 * ante_val
        self.set_stage(self.DISCOV_ST_CODE)

        # TODO should be deck.draw_cards(2) or smth
        self.dealer_hand.extend((
            StdCard.draw_card(), StdCard.draw_card()
        ))
        self.player_hand.extend((
            StdCard.draw_card(), StdCard.draw_card()
        ))
        self.pev(MyEvTypes.CardsReveal)
        self.pev(MyEvTypes.CashChanges, value=self.cash)

    def input_choice(self, is_betting):  # 0 or 1
        if self.stage == self.FLOP_ST_CODE:
            # betting => betx2, or check
            self.turnriver_cards.extend([StdCard.draw_card(), StdCard.draw_card()])
            self.revealed['turn'] = self.revealed['river'] = True
            self.set_stage(self.TR_ST_CODE)

        elif self.stage == self.TR_ST_CODE:
            # betting => betx1, or FOLD
            self.set_stage(self.OUTCOME_ST_CODE)

            self.revealed['dealer1'] = self.revealed['dealer2'] = True
            self.pev(MyEvTypes.CardsReveal)
            # do .pev for this and use the controller instead
            # TODO
            self.money_handling()

        elif self.stage == self.OUTCOME_ST_CODE:
            self.new_round()

    def new_round(self):  # like a reset
        self.set_stage(self.INIT_ST_CODE)
        for lname in self.revealed.keys():
            self.revealed[lname] = False  # hide all
        # remove all cards previously dealt
        del self.dealer_hand[:]
        del self.player_hand[:]
        del self.flop_cards[:]
        del self.turnriver_cards[:]

        self.pev(MyEvTypes.CardsReveal)

    def money_handling(self):
        # to be called when we're in the very last state
        # test win/loose conditions
        pass

    def input_init_choice(self, code_option):  # {0,...,2} -> check, bet3x, bet4x
        if self.stage != self.DISCOV_ST_CODE:
            raise ValueError('cannot input players initial choice while state isnt DISCOV')
        print(' **  EVO model - stage=2  ** ')
        for k in range(1, 3+1):
            self.revealed[f'flop{k}'] = True
        self.flop_cards.extend([StdCard.draw_card() for _ in range(3)])
        self.set_stage( self.FLOP_ST_CODE)
        self.pev(MyEvTypes.CardsReveal)

    def is_player_broke(self):
        return self.cash <= 0
