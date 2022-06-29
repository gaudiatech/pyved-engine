import katagames_engine as kengi
from pokerdefs import MyEvTypes
from tabletop import StandardCard, PokerHand

print(PokerHand)
EngineEvTypes = kengi.event.EngineEvTypes


class MoneyInfo(kengi.event.CogObj):
    """
    created a 2nd class (model) so it will be easier to manage
    earning & loosing

    earning := prize due to "Ante" + prize due to "Bet" + prize due to "Blind"

    right now this class isnt used, but it should become active
    """
    def __init__(self):
        super().__init__()
        self.cash = 200  # starting cash
        # TODO complete the implem & use this class!


class UthModel(kengi.event.CogObj):
    INIT_ST_CODE, DISCOV_ST_CODE, FLOP_ST_CODE, TR_ST_CODE, OUTCOME_ST_CODE, WAIT_STATE = range(1, 6 + 1)

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
        self.bet_factor = 0

        self.delta_money = 0
        self.folded = False

        self.autoplay_flag = False
        self.dealer_vhand = self.player_vhand = None

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
    def evolve_state(self, with_fold=None):
        if with_fold is None:
            with_fold = self.folded
        if self.DISCOV_ST_CODE == self.stage:
            self.go_flop()
        elif self.FLOP_ST_CODE == self.stage:
            self.go_tr_state()
        elif self.TR_ST_CODE == self.stage:
            self.go_outcome_state(with_fold)
        elif self.OUTCOME_ST_CODE == self.stage:
            self.go_wait_state()

    def set_stage(self, sid):
        assert 1 <= sid <= 6
        self._stage = sid
        print(f' --new state-- >>> {sid}')
        self.pev(MyEvTypes.StageChanges)

    def go_discov(self, ante_val):
        if self.stage != UthModel.INIT_ST_CODE:
            raise ValueError('calling deal_cards while model isnt in the initial state')
        self.revealed['player2'] = self.revealed['player1'] = True
        # TODO should be deck.draw_cards(2) or smth
        self.dealer_hand.extend((
            StandardCard.at_random(), StandardCard.at_random()
        ))
        self.player_hand.extend((
            StandardCard.at_random(), StandardCard.at_random()
        ))
        self.pay_to_play(ante_val)

        self.set_stage(self.DISCOV_ST_CODE)

    def go_flop(self):
        print('GO FLOP STATE')
        for k in range(1, 3 + 1):
            self.revealed[f'flop{k}'] = True
        self.flop_cards.extend([StandardCard.at_random() for _ in range(3)])
        self.set_stage(self.FLOP_ST_CODE)

    def go_tr_state(self):
        print('GO TR STATE')
        # betting => betx2, or check
        self.turnriver_cards.extend([StandardCard.at_random(), StandardCard.at_random()])
        self.revealed['turn'] = self.revealed['river'] = True
        self.set_stage(self.TR_ST_CODE)

    def describe_pl_hand(self):
        return self.player_vhand.description
        #print(f'  player has {player_vhand.description}   (score: {player_vhand.value}')
        #print(' > ')

    def describe_dealers_hand(self):
        return self.dealer_vhand.description
        # print(f'  dealer has {dealer_vhand.description}   (score: {dealer_vhand.value}')

    def go_outcome_state(self, with_fold):
        # performs computations to know & save what's the outcome
        print('GO OUTCOME STATE')
        self.folded = with_fold
        if not self.folded:
            # imagine we only consider the flop, for now
            # TODO complete this part
            self.player_vhand = PokerHand(self.player_hand + self.flop_cards)
            self.dealer_vhand = PokerHand(self.dealer_hand + self.flop_cards)
            if self.player_vhand.value > self.dealer_vhand.value:
                self.compute_gain()
            else:
                # compute loss
                self.delta_money = -self.ante - self.blind - self.bet
        else:
            self.delta_money = 0

        self.set_stage(self.OUTCOME_ST_CODE)

    def go_wait_state(self):
        # state dedicated to blit the type of hand (Two pair, Full house etc) + the outcome
        print('autoplay OFF!')
        self.autoplay_flag = False
        if not self.folded:
            self.revealed['dealer1'] = self.revealed['dealer2'] = True
        self.set_stage(self.WAIT_STATE)

    def new_round(self):  # like a reset
        # manage money:
        # TODO could use .pev here, if animations are needed
        #  it can be nice. To do so one would use the controller instead of lines below
        if self.folded:
            self.loose_money()
        else:
            a, b = self.player_vhand.value, self.dealer_vhand.value
            if a <= b:
                if a == b:
                    print('EGALITé')
                    self.refund_money()
                else:
                    print('JAI PERDU')
                    self.loose_money()
            else:
                print('JE BATS DEALER')
                self.earn_money()
        # reset folded flag
        self.folded = False

        # HIDE cards
        for lname in self.revealed.keys():
            self.revealed[lname] = False

        # remove all cards previously dealt
        del self.dealer_hand[:]
        del self.player_hand[:]
        del self.flop_cards[:]
        del self.turnriver_cards[:]

        self.set_stage(self.INIT_ST_CODE)

    def input_bet(self, small_or_big):  # accepted values: {0, 1}
        bullish_choice = small_or_big + 1
        if self.stage == self.INIT_ST_CODE:
            self.go_discov(4)  # 4 is the arbitrary val chosen for 'Ante', need to pick a val that can be
            # paid via chips available on the virtual game table. value 5 would'nt work!
        else:
            if self.stage == self.DISCOV_ST_CODE:
                if bullish_choice == 1:
                    self.bet_factor = 3
                    self.bet = self.bet_factor*self.ante
                else:
                    self.bet_factor = 4
                    self.bet = self.bet_factor*self.ante
            elif self.stage == self.FLOP_ST_CODE:
                self.bet_factor = 2
                self.bet = self.bet_factor*self.ante
            elif self.stage == self.TR_ST_CODE:
                self.bet_factor = 1
                self.bet = self.ante
            self.cash -= self.bet
            self.pev(MyEvTypes.CashChanges, value=self.cash)
            self.pev(MyEvTypes.EndRoundRequested, folded=False)

    def input_check(self):
        # doing the CHECK only
        if self.stage == self.DISCOV_ST_CODE:
            self.go_flop()

        elif self.stage == self.FLOP_ST_CODE:
            self.go_tr_state()

        elif self.stage == self.TR_ST_CODE:
            self.pev(MyEvTypes.EndRoundRequested, folded=True)

        elif self.stage == self.WAIT_STATE:
            self.new_round()

    # ---------------------------------
    #  money handling
    # ---------------------------------
    def test_if_players_broke(self):
        if self.cash <= 0:
            self.pev(EngineEvTypes.GAMEENDS)

    def pay_to_play(self, x):
        self.ante = self.blind = x
        self.cash -= 2 * x
        self.pev(MyEvTypes.CashChanges, value=self.cash)

    def compute_gain(self):
        # calcul gain spécifique & relatif à la blinde
        # -------------------------------------------
        # Royal flush- 500 pour 1
        # Straigth flush- 50 pour 1
        # Four of a kind - 10 pour 1
        # Full house - 3 pour 1
        # Flush - 1.5 pour 1
        # Suite - 1 pour 1
        # autres mains y a pas eu victore mais simple égalité!
        multiplicateur = {
            'High Card': 0,
            'One Pair': 0,
            'Two Pair': 0,
            'Straight': 1,
            'Flush': 1.5,
            'Full House': 3,
            'Four of a Kind': 10,
            'Straight Flush': 50
        }[self.describe_pl_hand()]
        self.delta_money = self.blind * multiplicateur

    def refund_money(self):
        self.cash += self.ante + self.blind + self.bet
        self.ante = self.blind = self.bet = 0  # reset-like
        self.pev(MyEvTypes.CashChanges, value=self.cash)

    def earn_money(self):
        self.refund_money()
        self.cash += self.delta_money
        self.pev(MyEvTypes.CashChanges, value=self.cash)

    def loose_money(self):
        self.delta_money = -self.ante - self.blind - self.bet
        self.ante = self.blind = self.bet = 0  # reset-like
        self.pev(MyEvTypes.CashChanges, value=self.cash)
