import katagames_engine as kengi
from pokerdefs import MyEvTypes
from tabletop import StdCard, PokerHand

print(PokerHand)
EngineEvTypes = kengi.event.EngineEvTypes


class UthModel(kengi.event.CogObj):
    INIT_ST_CODE, DISCOV_ST_CODE, FLOP_ST_CODE, TR_ST_CODE, OUTCOME_ST_CODE = range(1, 5 + 1)

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
        self.bet = 0

        self.autoplay_flag = False

        # stored lists of cards
        self.dealer_hand = []
        self.player_hand = []
        self.flop_cards = []
        self.turnriver_cards = []

        self._stage = None
        self.set_stage(self.INIT_ST_CODE)

    # avoid external modification of stage => encapsulate data
    @property
    def stage(self):
        return self._stage

    # -----------------------
    #  state transitions
    # -----------------------
    def evolve_state(self):
        if self.DISCOV_ST_CODE == self.stage:
            self.go_flop()
        elif self.FLOP_ST_CODE == self.stage:
            self.go_tr_state()
        elif self.TR_ST_CODE == self.stage:
            self.go_outcome_state()

    def set_stage(self, sid):
        assert 1 <= sid <= 5
        self._stage = sid
        print(f' --new state-- >>> {sid}')
        self.pev(MyEvTypes.StageChanges)

    def go_discov(self, ante_val):
        if self.stage != UthModel.INIT_ST_CODE:
            raise ValueError('calling deal_cards while model isnt in the initial state')
        self.revealed['player2'] = self.revealed['player1'] = True
        self.ante = self.blind = ante_val
        self.cash -= 2 * ante_val
        # TODO should be deck.draw_cards(2) or smth
        self.dealer_hand.extend((
            StdCard.draw_card(), StdCard.draw_card()
        ))
        self.player_hand.extend((
            StdCard.draw_card(), StdCard.draw_card()
        ))
        self.pev(MyEvTypes.CashChanges, value=self.cash)
        self.set_stage(self.DISCOV_ST_CODE)

    def go_flop(self):
        print('GO FLOP STATE')
        for k in range(1, 3 + 1):
            self.revealed[f'flop{k}'] = True
        self.flop_cards.extend([StdCard.draw_card() for _ in range(3)])
        self.set_stage(self.FLOP_ST_CODE)

    def go_tr_state(self):
        print('GO TR STATE')
        # betting => betx2, or check
        self.turnriver_cards.extend([StdCard.draw_card(), StdCard.draw_card()])
        self.revealed['turn'] = self.revealed['river'] = True
        self.set_stage(self.TR_ST_CODE)

    def go_outcome_state(self):
        print('GO OUTCOME STATE')
        # TODO blit the type of hand (Two pair, Full house etc) + the score val.
        self.revealed['dealer1'] = self.revealed['dealer2'] = True
        self.autoplay_flag = False
        print('autoplay OFF!')
        self.set_stage(self.OUTCOME_ST_CODE)

        # manage money:
        # TODO could use .pev here, if animations are needed
        #  it can be nice. To do so one would use the controller instead of lines below
        has_won = False
        if has_won:
            self.earn_money()
        else:
            self.loose_money()

    def new_round(self):  # like a reset
        for lname in self.revealed.keys():
            self.revealed[lname] = False  # hide all
        # remove all cards previously dealt
        del self.dealer_hand[:]
        del self.player_hand[:]
        del self.flop_cards[:]
        del self.turnriver_cards[:]
        self.set_stage(self.INIT_ST_CODE)

    def input_choice(self, bullish_choice):  # accepted values: {0, 1, 2}
        if bullish_choice > 0:
            if self.stage == self.INIT_ST_CODE:
                self.go_discov(4)  # 4 is the arbitrary val chosen for 'Ante', need to pick a val that can be
                # paid via chips available on the virtual game table. value 5 would'nt work!
            else:
                self.pev(MyEvTypes.PlayerBets)
        else:
            if self.stage == self.DISCOV_ST_CODE:
                self.go_flop()

            elif self.stage == self.FLOP_ST_CODE:
                self.go_tr_state()

            elif self.stage == self.TR_ST_CODE:
                self.new_round()

            if self.stage == self.OUTCOME_ST_CODE:
                self.new_round()

    # ---------------------------------
    #  money handling
    # ---------------------------------
    def test_if_players_broke(self):
        if self.cash <= 0:
            self.pev(EngineEvTypes.GAMEENDS)

    def earn_money(self):
        # to be called when we're in the very last state
        # test win/loose conditions
        pass

    def loose_money(self):
        pass
