from pokerbundle import common

# import katagames_sdk as katasdk
import random

# ------------------------------------
#  ALIASES
# ------------------------------------
# kengi = katasdk.kengi
import pyved_engine as pyv

Card = pyv.tabletop.StandardCard
CardDeck = pyv.tabletop.CardDeck
find_best_ph = pyv.tabletop.find_best_ph
Label = pyv.gui.Label
MyEvTypes = common.MyEvTypes
PokerHand = pyv.tabletop.PokerHand
pygame = pyv.pygame
StandardCard = pyv.tabletop.StandardCard
wContainer = pyv.gui.WidgetContainer

# ------------------------------------
#  CONSTANTS
# ------------------------------------
WARP_BACK = [2, 'niobepolis']
CARD_SIZE_PX = (69, 101)
CST_VSPACING_BT = 4
CST_HSPACING_BT = 10  # buttons that are actual player controls, at every pokerstate
OVERLAY_POS = (85, 35)
CHIP_SIZE_PX = (33, 33)
BACKGROUND_IMG_PATH = 'user_assets/pokerbackground3.png'
OFFSET_CASH = (-48, -24)
BASE_X_CARDS_DR = 326
Y_CARDS_DRAWN = 132
CRD_OFFSET = 43
MLABELS_POS = {
    'trips': (243, 175),
    'play': (231, 246),
    'ante': (214, 215),
    'blind': (258, 215),
    'cash': (10, 170),
    'e_trips': (210, 175),
    'e_play': (231, 234),
    'e_ante': (214, 205),
    'e_blind': (258, 205),
}
DIM_DROPZONES = [
    (70, 30),
    (112, 24)
]
# coords in pixel -> where to place cards/chips
CARD_SLOTS_POS = {
    'dealer1': (241, 60),
    'dealer2': (241 + CRD_OFFSET, 60),
    'flop3': (BASE_X_CARDS_DR - 2 * CRD_OFFSET, Y_CARDS_DRAWN),
    'flop2': (BASE_X_CARDS_DR - 1 * CRD_OFFSET, Y_CARDS_DRAWN),
    'flop1': (BASE_X_CARDS_DR, Y_CARDS_DRAWN),
    'river': (BASE_X_CARDS_DR - 3 * CRD_OFFSET, Y_CARDS_DRAWN),
    'turn': (BASE_X_CARDS_DR - 4 * CRD_OFFSET, Y_CARDS_DRAWN),
    'player1': (111, 215),
    'player2': (111 + CRD_OFFSET, 215),
}
MONEY_POS = {
    'ante': (45, 166),
    'blind': (90, 166),
    'raise1': (955 / 3, 870 / 3),
    'raise2': (961 / 3, 871 / 3),
    'raise3': (967 / 3, 872 / 3),
    'raise4': (973 / 3, 873 / 3),
    'raise5': (980 / 3, 875 / 3),
    'raise6': (986 / 3, 876 / 3)
}
PLAYER_CHIPS = {
    '2a': (238, 278),  # the only cst value used rn
    '2b': (905 / 2, 1000 / 2),
    '5': (985 / 2, 1000 / 2),
    '10': (1065 / 2, 1000 / 2),
    '20': (1145 / 2, 1000 / 2)
}
CHIP_SELECTOR_POS = (168, 295)
STATUS_MSG_BASEPOS = (8, 258)


class WalletModel(pyv.Emitter):
    """
    This class handles (in the model) everything that’s related to money.
    What events are used?
    - MoneyUpdate
    - ChipUpdate
    """

    def __init__(self, wealth):
        super().__init__()
        self._wealth = wealth
        self.prev_victorious = 0
        self.prev_total_bet = None

        # this value can be chosen by the player. Ideally this should be measured in CR,
        # as soon as the Uth game is active within the Ktg system
        self.__curr_chip_val = 2

        # indique le dernier changement récent ds la richesse & repartition gains
        self.delta_wealth = 0
        self.prev_earnings = None

        # during the match
        self.bets = {
            'trips': 0,
            'ante': 0,
            'blind': 0,
            'play': 0
        }
        self.ready_to_start = False

    @property
    def curr_chipval(self):
        return self.__curr_chip_val

    @curr_chipval.setter
    def curr_chipval(self, newvalue):
        self.__curr_chip_val = newvalue
        self.pev(MyEvTypes.ChipUpdate, value=self.__curr_chip_val)

    def can_stack(self, trips=False):
        if trips:
            return self.__curr_chip_val <= self._wealth
        else:
            if (self._wealth - 2 * self.__curr_chip_val) < 0:
                return False
            return True

    def stack_chip(self, trips=False):
        if trips:
            self.bets['trips'] += self.__curr_chip_val
            self.delta_wealth = self.__curr_chip_val
        else:
            self.bets['ante'] += self.__curr_chip_val
            self.bets['blind'] += self.__curr_chip_val
            self.delta_wealth = 2 * self.__curr_chip_val

        self._wealth -= self.delta_wealth
        self.pev(MyEvTypes.MoneyUpdate, value=self._wealth)

    def reset_bets(self, collect_mode=0):
        if collect_mode == 0:
            pass
        elif collect_mode == 1:
            clawback = self.bets['ante'] + self.bets['trips']
            self._wealth += clawback
        elif collect_mode == 2:
            clawback = self.bets['ante'] + self.bets['trips'] + self.bets['trips']
            self._wealth += clawback

        for bslot in self.bets.keys():
            self.bets[bslot] = 0
        self.pev(common.MyEvTypes.MoneyUpdate, value=self._wealth)

    def select_trips(self, val):
        self.bets['trips'] = val
        self.pev(common.MyEvTypes.BetUpdate)

    @property
    def all_infos(self):
        return self.bets['trips'], self.bets['ante'], self.bets['blind'], self.bets['play']

    def get_balance(self):
        return self._wealth

    def bet(self, multiplier):
        """
        before the flop :   3x or 4x ante
        at the flop     :   2x ante
        at the turn&river:  1x ante
        """
        assert isinstance(multiplier, int) and 0 < multiplier < 5
        self.bets['play'] = multiplier * self.bets['ante']
        self._wealth -= self.bets['play']
        self.pev(MyEvTypes.MoneyUpdate, value=self._wealth)

    def resolve(self, pl_vhand, dealer_vhand):
        """
        en fin de partie on peut appeler cette fonction qui va determiner quelle suite à donner
        (l’impact sur l’argent du joueur)
        de la fin de partie ...

        Algo pseudo-code:
        * si égalité, les mises restent aux joueurs sans gain ni perte
        (cas particulier pour le Bonus, voir ci-dessous)

        * si Dealer vhand > Player vhand
        alors dealer recupere tt les mises des cases « Mise (Ante) »,« Blinde »,  et « Play »

        * Si Player vhand > Dealer vhand
        alors player récupère l’intégralité de ses mises de départ
        + ses enjeux seront récompensés en fct du tableau de paiement indiqué +haut
        """
        player_sc, dealer_sc = pl_vhand.value, dealer_vhand.value

        self.prev_total_bet = sum(tuple(self.bets.values()))
        self.prev_victorious = 0
        if player_sc < dealer_sc:
            return -1

        self.prev_victorious = 1
        if player_sc == dealer_sc:
            # give back bets
            self.prev_earnings = sum(tuple(self.bets.values()))
            return 0

        # gere money aussi
        winner_vhand = pl_vhand
        earnings = self.bets.copy()
        a = earnings['play']
        earnings['play'] += a
        b = earnings['ante']
        earnings['ante'] += b
        earnings['blind'] = c = WalletModel.comp_blind_payout(self.bets['blind'], winner_vhand)
        d = WalletModel.comp_trips_payout(self.bets['trips'], winner_vhand)
        earnings['trips'] = d
        self.prev_earnings = sum(tuple(earnings.values()))
        self.prev_gain = sum((a, b, c, d))
        return 1

    def impact_fold(self):
        """
        dealers does not qualify if dealer's hand is less than a pair!
        when this happens, the ante bet is "pushed"
        """
        # if not dealer_qualifies:
        #     self._wealth += self.bets['ante']
        self.prev_total_bet = sum(tuple(self.bets.values()))
        self.prev_victorious = 0

        self.reset_bets(0)
        self.pev(MyEvTypes.MoneyUpdate, value=self._wealth)

    def collect_case_victory(self):
        if self.prev_victorious:
            self._wealth += self.prev_earnings
            self.pev(MyEvTypes.MoneyUpdate, value=self._wealth)

    @staticmethod
    def comp_trips_payout(x, winning_vhand):
        """
        the "Trips" bet
        ---------------
        Royal Flush/Quinte Royale   -> 50:1
        Straight Flush/Quinte       -> 40:1
        Four of a kind/Carré        -> 30:1
        Full/Main pleine            -> 8:1
        Flush/Couleur               -> 7:1
        Straight/Suite              -> 4:1
        Three of a kind/Brelan      -> 3:1
        :return: y
        """
        y = 0
        if winning_vhand.is_royal():
            y += 50 * x
        elif winning_vhand.is_straight() and winning_vhand.is_flush():  # straight Flush
            y += 40 * x
        elif winning_vhand.is_four_oak():
            y += 30 * x
        elif winning_vhand.is_full():
            y += 8 * x
        elif winning_vhand.is_flush():
            y += 7 * x
        elif winning_vhand.is_straight():
            y += 4 * x
        elif winning_vhand.is_trips():
            y += 3 * x
        return y

    @staticmethod
    def comp_blind_payout(x, winning_vhand):
        """
        ---------------the "Blind" bet---------------
        Royal Flush/Quinte Royale   -> 500:1
        Straight Flush/Quinte       -> 50:1
        Four of a kind/Carré        -> 10:1
        Full/Main pleine            -> 3:1 (x3)
        Flush/Couleur               -> 3:2 (x1.5)
        Straight/Suite              -> 1:1
        """
        if winning_vhand.is_royal():
            return 500 * x
        # straight Flush detection
        if winning_vhand.is_straight() and winning_vhand.is_flush():
            return 50 * x
        if winning_vhand.is_four_oak():
            return 10 * x
        if winning_vhand.is_full():
            return 3 * x
        if winning_vhand.is_flush():
            return int(1.5 * x)
        if winning_vhand.is_straight():
            return x
        return 0

    def is_player_broke(self):
        """
        useful method because someone may want to call .pev(EngineEvTypes.GAMEENDS) when player's broke
        :return: True/False
        """
        return self._wealth <= 0


def hackfromcli_side(delta_w):  # wealth

    return 0  # nothing to do bc I exec this in local Ctx, ONLY AS A TEST

    connector = katasdk.get_pyconnector()
    # print(delta_w)
    # print(connector.stored_pid)

    # un peu obfusk
    if connector.is_logged:
        serv = connector.network.get_link()
        y = ''
        while random.randint(0, 7) != 0:
            y += random.choice(('a', 'Z', 'y', 'B', 'u', 'U', 't', 'm', 'l'))
        if delta_w > 0:
            s = random.choice(('g', 'e', 'w'))
        else:
            s = 'r'  # retire /retrait
        x = list(str(abs(delta_w)).zfill(4))
        y += x[-1]
        y += x[-2]
        y += x[-3]
        y += x[-4]
        y += s
        print(y)
        target = serv.get_gtm_app_url() + 'ekar.php'
        params = {
            'id_perso': connector.stored_pid,
            'updating': 1,
            'pkout': y
        }
        serv.proxied_get(target, params)
        # tmp = json.loads(res)
        # if tmp is None:
        #     raise Exception("Can't retrieve player's balance!")
        # else:
        #     return int(tmp)


class UthModel(pyv.Emitter):
    """
    Uth: Ultimate Texas Holdem
    this is a model class, it handles "poker states" (mostly)
    """

    def __init__(self):
        super().__init__()

        # c = katasdk.get_pyconnector()  # link with CR and use the real wealth value
        # ub = c.get_user_balance()
        ub = 100
        self.wallet = WalletModel(ub)

        self.match_over = False
        self.bet_done = False
        self.player_folded = False

        self.result = None

        # ---------------
        # CARD MANAGEMENT
        # ---------------
        self.deck = CardDeck()
        self.visibility = {
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
        # temp attributes to save best virtual hand (5 cards chosen out of 7)
        self.dealer_vhand = self.player_vhand = None

        # stored lists of cards
        self.dealer_hand = []
        self.player_hand = []
        self.flop_cards = []
        self.turnriver_cards = []

        # ----------------
        # STATE MANAGEMENT
        # ----------------
        self._pokerstate = None
        self.possible_bet_factor = None  # will be [3, 4] then [2, ] then [1, ]
        self._goto_next_state()

    @property
    def autoplay(self):
        return self.bet_done or self.player_folded

    def quantify_reward(self):
        return self.wallet.prev_gain

    def get_card_code(self, info):
        """
        can be anythin in [
         dealer1, dealer2, player1, player2, flop3, flop2, flop1,
         river, turn
        ]
        """
        if info == 'dealer1':
            return self.dealer_hand[0].code
        if info == 'dealer2':
            return self.dealer_hand[1].code
        if info == 'player1':
            return self.player_hand[0].code
        if info == 'player2':
            return self.player_hand[1].code
        if info == 'flop3':
            return self.flop_cards[2].code
        if info == 'flop2':
            return self.flop_cards[1].code
        if info == 'flop1':
            return self.flop_cards[0].code
        if info == 'turn':
            return self.turnriver_cards[0].code
        if info == 'river':
            return self.turnriver_cards[1].code
        raise ValueError('unrecognized >info< argument passed to UthModel.get_card_code')

    @property
    def stage(self):
        return self._pokerstate

    def get_chipvalue(self):
        return self.wallet.curr_chipval

    def set_chipvalue(self, newv):
        self.wallet.curr_chipval = newv

    def get_balance(self):
        return self.wallet.get_balance()

    def get_all_bets(self):
        return self.wallet.all_infos

    def _proc_state(self, newstate):
        if newstate == common.PokerStates.AnteSelection:
            self.possible_bet_factor = None
            # self.init_new_round()

        elif newstate == common.PokerStates.PreFlop:
            print('hi im in preflop')
            self.possible_bet_factor = [3, 4]
            # cards have been dealt !
            self.wallet.ready_to_start = True

            # TODO should be deck.draw_cards(2) or smth
            self.dealer_hand.extend(self.deck.deal(2))
            self.player_hand.extend(self.deck.deal(2))
            self.visibility['player2'] = self.visibility['player1'] = True

        elif newstate == common.PokerStates.Flop:
            print('hi im in the flop state')
            self.possible_bet_factor = [2, ]
            for k in range(1, 3 + 1):
                self.visibility[f'flop{k}'] = True
            self.flop_cards.extend(self.deck.deal(3))

        elif newstate == common.PokerStates.TurnRiver:
            print('eee im in the TurnRiver state')
            self.possible_bet_factor = [1, ]
            # betting => betx2, or check
            self.turnriver_cards.extend(self.deck.deal(2))
            self.visibility['turn'] = self.visibility['river'] = True

        elif newstate == common.PokerStates.Outcome:
            self.possible_bet_factor = None
            self.visibility['dealer1'] = self.visibility['dealer2'] = True

            # state dedicated to blit the type of hand (Two pair, Full house etc) + the outcome
            if self.player_folded:
                self.result = -1
                self.wallet.impact_fold()

            else:
                self.dealer_vhand = find_best_ph(self.dealer_hand + self.flop_cards + self.turnriver_cards)
                self.player_vhand = find_best_ph(self.player_hand + self.flop_cards + self.turnriver_cards)
                self.result = self.wallet.resolve(self.player_vhand, self.dealer_vhand)

            self.match_over = True
            self.pev(MyEvTypes.MatchOver, won=self.result)

    def _goto_next_state(self):
        """
        iterate the game (pure game logic)

        !! for a much cleaner structure, this should be done via
         --- a set of (GameStates, controller) pairs ---
        TODO refactoring Uth
        """
        if self._pokerstate is None:
            self.init_new_round()
        pks = common.PokerStates
        tr_table = {
            None: pks.AnteSelection,
            pks.AnteSelection: pks.PreFlop,
            pks.PreFlop: pks.Flop,
            pks.Flop: pks.TurnRiver,
            pks.TurnRiver: pks.Outcome,
            pks.Outcome: None
        }
        self._pokerstate = tr_table[self._pokerstate]

        # since February, the model should not decide what game state we are in,
        # let controllers do this job !
        # TODO finish the refactoring
        # - specific update of the model !!!
        self._proc_state(self._pokerstate)  # these actions should probably be moved to specific controllers

    def check(self):
        self._goto_next_state()

    def fold(self):
        self.player_folded = True
        self._goto_next_state()

    @property
    def pl_hand_description(self):
        return self.player_vhand.description

    @property
    def dl_hand_description(self):
        return self.dealer_vhand.description

    def init_new_round(self):
        print('-------------model init new round --------------------')
        self.match_over = False
        self.wallet.reset_bets(int(self.wallet.prev_victorious))

        del self.dealer_hand[:]
        del self.player_hand[:]
        del self.flop_cards[:]
        del self.turnriver_cards[:]

        for lname in self.visibility.keys():
            self.visibility[lname] = False

        self.deck.reset()
        self.bet_done = False
        self.player_folded = False
        self.pev(MyEvTypes.NewMatch)

    def select_bet(self, bullish_choice=False):
        if bullish_choice and self._pokerstate != common.PokerStates.PreFlop:
            raise RuntimeError('non valid bullish_choice argument detected!')
        b_factor = self.possible_bet_factor[0]
        if bullish_choice:
            b_factor = self.possible_bet_factor[1]
        self.wallet.bet(b_factor)
        self.bet_done = True

        self._goto_next_state()
        self.pev(MyEvTypes.RienNeVaPlus)


class UthView(pyv.EvListener):
    TEXTCOLOR = pyv.pal.punk['flashypink']
    BG_TEXTCOLOR = (92, 92, 100)
    ASK_SELECTION_MSG = 'SELECT ONE OPTION: '

    def __init__(self, model):
        super().__init__()
        self.debug_drag_n_drop = False

        self._rect_dropzone_li = [
            pygame.Rect(MLABELS_POS['trips'], DIM_DROPZONES[0]),
            pygame.Rect((0, 0), DIM_DROPZONES[1])
        ]
        # adjust drop zones
        self._rect_dropzone_li[0].top -= 10
        self._rect_dropzone_li[0].left -= 8
        self._rect_dropzone_li[1].topleft = MLABELS_POS['ante']
        self._rect_dropzone_li[1].top -= 5
        for dzo in self._rect_dropzone_li:
            dzo.left -= 8

        self.overlay_spr = pygame.image.load('user_assets/overlay0.png')
        self.overlay_spr.set_colorkey((255, 0, 255))

        self.bg = None
        self._my_assets = dict()

        self.chip_spr = dict()
        self.adhoc_chip_spr = None
        self.dragged_chip_pos = None

        self._assets_rdy = False
        self._mod = model

        self.pokergame_ft = pyv.gfx.JsonBasedCfont(
            'user_assets/capello-ft'
        )  # EmbeddedCfont() #pyv.pygame.font.Font(None, 20)

        # if local ctx
        # local_ctx = not katasdk.webctx_flag()
        local_ctx = True
        if local_ctx:
            self.pokergame_ft.forcing_transparency = True

        self.info_msg0 = None
        self.info_msg1 = None  # will be used to tell the player what he/she has to do!
        self.info_messages = list()

        self.scrsize = pyv.get_surface().get_size()
        self.midpt = [self.scrsize[0] // 2, self.scrsize[1] // 2]

        self._chips_related_wcontainer = self._build_chips_related_gui()
        # no need to debug (feb 25th)
        # self._chips_related_wcontainer.set_debug_flag()

        # self._chips_related_wcontainer.set_debug_flag()
        self.chip_scr_pos = tuple(PLAYER_CHIPS['2a'])
        self._gui_labels = None
        self._mlabels = None
        self._do_gui_labels()
        self._do_set_money_labels()  # replace prev. line by a meaningful dict

        self.act_deal_cards = None
        self.act_undo_stake = None
        self.act_bet_same = None
        self.act_clear_chips = None
        self._act_related_wcontainer = self._init_actions_related_gui()
        # force affichage du W. container
        # self._act_related_wcontainer.set_debug_flag()

        self.generic_wcontainer = wContainer(
            (320, 244), (133, 250), wContainer.FLOW,
            [
                pyv.gui.Button2(None, 'Bet x4', (0, 0), tevent=MyEvTypes.BetHighDecision),
                pyv.gui.Button2(None, 'Bet x3', (0, 0), tevent=MyEvTypes.BetDecision),
                pyv.gui.Button2(None, 'Check', (0, 0), tevent=MyEvTypes.CheckDecision)
            ],
            spacing=CST_HSPACING_BT,
            vspacing=CST_VSPACING_BT
        )

        self.on_money_update(None)  # force a 1st money update

    def _do_gui_labels(self):
        self._gui_labels = {
            'trips_etq': Label(MLABELS_POS['e_trips'], 'Trips', None, replacemt_ft=self.pokergame_ft),
            'ante_etq': Label(MLABELS_POS['e_ante'], 'Ante', None, replacemt_ft=self.pokergame_ft),
            'blind_etq': Label(MLABELS_POS['e_blind'], 'Blind', None, replacemt_ft=self.pokergame_ft),
            'play_etq': Label(MLABELS_POS['e_play'], 'Play', None, replacemt_ft=self.pokergame_ft),
        }

    def _do_set_money_labels(self):
        # ftsize_mlabels = 17
        self._mlabels = {
            # 'trips_etq': Label(MLABELS_POS['trips'], 'trips?', ftsize_mlabels),
            'trips_etq': Label(MLABELS_POS['trips'], 'trips?', None, replacemt_ft=self.pokergame_ft),
            'ante_etq': Label(MLABELS_POS['ante'], 'ante?', None, replacemt_ft=self.pokergame_ft),
            'blind_etq': Label(MLABELS_POS['blind'], 'blind?', None, replacemt_ft=self.pokergame_ft),
            'play_etq': Label(MLABELS_POS['play'], 'play?', None, replacemt_ft=self.pokergame_ft),
            'cash_etq': Label(MLABELS_POS['cash'], 'cash?', None, replacemt_ft=self.pokergame_ft),  # 4+ftsize_mlabels
        }

    def _build_chips_related_gui(self):  # TODO group with other obj so we have 1 panel dedicated to AnteSelection
        # - cycle right button
        def cb0():
            pyv.get_ev_manager().post(MyEvTypes.CycleChipval, upwards=True)

        cycle_r_button = pyv.gui.Button2(None, '>', (0, 0), callback=cb0)

        # - cycle left button
        def cb1():
            pyv.get_ev_manager().post(MyEvTypes.CycleChipval, upwards=False)

        cycle_l_button = pyv.gui.Button2(None, '<', (0, 0), callback=cb1)

        # disabled this, since Drag N Drop is working now
        # stake_button = pyv.gui.Button2(None, ' __+__ ', (0, 0), tevent=MyEvTypes.StackChip)

        chip_related_buttons = [
            cycle_l_button,
            # stake_button,
            cycle_r_button,
        ]
        targ_w = 140
        return wContainer(
            CHIP_SELECTOR_POS,
            (targ_w, 32),
            wContainer.EXPAND,
            chip_related_buttons, spacing=8
        )

    @staticmethod
    def _init_actions_related_gui():
        all_bt = [
            pyv.gui.Button2(None, 'Bet_Same', (0, 11), tevent=MyEvTypes.BetIdem),  # bet same action is Bt #0

            pyv.gui.Button2(None, 'Deal', (330, 128), tevent=MyEvTypes.DealCards),
            pyv.gui.Button2(None, 'Undo', (0, 0), tevent=MyEvTypes.BetUndo),
            pyv.gui.Button2(None, 'Reset_Bet', (0, 0), tevent=MyEvTypes.BetReset),
        ]

        return wContainer(
            (390, 170),
            (60, 170),
            wContainer.FLOW, all_bt, spacing=CST_HSPACING_BT, vspacing=CST_VSPACING_BT
        )

    def show_anteselection(self):
        # ensure everything is reset
        del self.info_messages[:]
        self._chips_related_wcontainer.set_active()
        self._chips_related_wcontainer.content[0].set_enabled(True)
        self._chips_related_wcontainer.content[1].set_enabled(True)

        self._act_related_wcontainer.set_active()
        self._act_related_wcontainer.content[0].set_enabled(False)
        self._act_related_wcontainer.content[1].set_enabled(False)
        self._act_related_wcontainer.content[2].set_enabled(False)
        self._act_related_wcontainer.content[3].set_enabled(False)

    def hide_anteselection(self):
        # if self._chips_related_wcontainer.active:
        self._chips_related_wcontainer.set_active(False)
        # if self._act_related_wcontainer.active:
        self._act_related_wcontainer.set_active(False)

    def show_generic_gui(self):
        self.generic_wcontainer.set_active()
        # For extra- practicity, add custom getters to the object WidgetContainer that we use
        self.generic_wcontainer.bethigh_button = self.generic_wcontainer.content[0]
        self.generic_wcontainer.bet_button = self.generic_wcontainer.content[1]
        self.generic_wcontainer.check_button = self.generic_wcontainer.content[2]

    def hide_generic_gui(self):
        self.generic_wcontainer.set_active(False)

    def on_bet_reset(self, ev):
        self._mod.wallet.reset_bets(2)

    def on_chip_update(self, ev):
        # replace image in the sprite
        self.adhoc_chip_spr = self.chip_spr[str(ev.value)]

    def _load_assets(self):
        self.bg = pyv.pygame.image.load(BACKGROUND_IMG_PATH)
        spr_sheet = pyv.gfx.JsonBasedSprSheet('user_assets/pxart-french-cards')
        self._my_assets['card_back'] = spr_sheet['back-blue.png']
        for card_cod in StandardCard.all_card_codes():
            y = PokerHand.adhoc_mapping(card_cod[0]).lstrip('0') + card_cod[1].upper()  # convert card code to path
            self._my_assets[card_cod] = spr_sheet[f'{y}.png']
        spr_sheet2 = pyv.gfx.JsonBasedSprSheet('user_assets/pokerchips')

        for chip_val_info in ('2a', '2b', '5', '10', '20'):
            y = {
                '2a': 'chip02.png',
                '2b': 'chip02.png',
                '5': 'chip05.png',
                '10': 'chip10.png',
                '20': 'chip20.png'
            }[chip_val_info]  # adapt filename

            # no chip rescaling : tempimg = spr_sheet2[y]
            # chip rescaling:
            tempimg = pygame.transform.scale(spr_sheet2[y], CHIP_SIZE_PX)
            tempimg.set_colorkey((255, 0, 255))

            spr = pyv.pygame.sprite.Sprite()
            spr.image = tempimg
            spr.rect = spr.image.get_rect()
            spr.rect.center = PLAYER_CHIPS[chip_val_info]
            self.chip_spr['2' if chip_val_info in ('2a', '2b') else chip_val_info] = spr

        self.adhoc_chip_spr = self.chip_spr[str(self._mod.get_chipvalue())]
        self._assets_rdy = True

    def on_mousedown(self, ev):
        if self.adhoc_chip_spr.rect.collidepoint(
                ev.pos  # pyv.vscreen.proj_to_vscreen(ev.pos)
        ):
            self.dragged_chip_pos = list(self.adhoc_chip_spr.rect.center)

    def on_mouseup(self, ev):
        if self.dragged_chip_pos:
            for k, dzo in enumerate(self._rect_dropzone_li):
                if dzo.collidepoint(self.dragged_chip_pos):
                    if k == 0:
                        # if we ever hav a poker backend..
                        # self.pev(MyEvTypes.StackChip, trips=True)

                        # but, until then:
                        if self._mod.wallet.can_stack(True):
                            self._mod.wallet.stack_chip(True)
                    else:
                        # idem ..
                        # self.pev(MyEvTypes.StackChip, trips=False)
                        if self._mod.wallet.can_stack():
                            self._mod.wallet.stack_chip()

            self.dragged_chip_pos = None

    def on_mousemotion(self, ev):
        if self.dragged_chip_pos:
            self.dragged_chip_pos[0], self.dragged_chip_pos[1] = pyv.proj_to_vscreen(ev.pos)

    def on_money_update(self, ev):
        if self._act_related_wcontainer.active:
            bv = self._mod.wallet.bets['ante'] > 0
            for i in range(1, 4):  # all buttons except BetIdem
                self._act_related_wcontainer.content[i].set_enabled(bv)
        self._refresh_money_labels()

    def _refresh_money_labels(self):
        tripsv, antev, blindv, playv = self._mod.get_all_bets()
        x = self._mod.get_balance()

        self._mlabels['trips_etq'].text = f'%d CR' % tripsv
        self._mlabels['ante_etq'].text = f'%d CR' % antev
        self._mlabels['blind_etq'].text = f'%d CR' % blindv
        self._mlabels['play_etq'].text = f'%d CR' % playv

        self._mlabels['cash_etq'].text = f'Wealth: %d CR' % x

    def on_match_over(self, ev):
        self.info_msg2 = self.pokergame_ft.render('Click to restart', False, self.TEXTCOLOR)

        if ev.won == 0:  # tie
            self.info_msg0 = self.pokergame_ft.render('Its a Tie.', True, self.TEXTCOLOR)
            infoh_player = self._mod.player_vhand.description
            infoh_dealer = self._mod.dealer_vhand.description
            self.info_msg1 = None
            result = self._mod.quantify_reward()  # can win due to Trips, even if its a Tie
            self.info_messages = [
                self.pokergame_ft.render(f"Dealer: {infoh_dealer};", False, self.TEXTCOLOR),
                self.pokergame_ft.render(f"Player: {infoh_player};", False, self.TEXTCOLOR),
                self.pokergame_ft.render(f"Change: {result} CR", False, self.TEXTCOLOR),
            ]

        elif ev.won == 1:  # won indeed
            result = self._mod.quantify_reward()
            infoh_player = self._mod.player_vhand.description
            infoh_dealer = self._mod.dealer_vhand.description
            # msg = f"Player: {infoh_player}; Dealer: {infoh_dealer}; Change {result}$"
            self.info_msg0 = self.pokergame_ft.render('Victory!', False, self.TEXTCOLOR)
            self.info_msg1 = None
            self.info_messages = [
                self.pokergame_ft.render(f"Dealer: {infoh_dealer};", False, self.TEXTCOLOR),
                self.pokergame_ft.render(f"Player: {infoh_player};", False, self.TEXTCOLOR),
                self.pokergame_ft.render(f"Change: {result} CR", False, self.TEXTCOLOR),
            ]

        elif ev.won == -1:  # lost
            if self._mod.player_folded:
                msg = 'Player folded.'
            else:
                msg = 'Defeat.'
            self.info_msg0 = self.pokergame_ft.render(msg, True, self.TEXTCOLOR)
            result = -self._mod.wallet.prev_total_bet
            if self._mod.player_folded:
                self.info_msg1 = self.pokergame_ft.render(f"You lost {-result} CR", False, self.TEXTCOLOR)
            else:
                infoh_dealer = self._mod.dealer_vhand.description
                infoh_player = self._mod.player_vhand.description
                self.info_messages = [
                    self.pokergame_ft.render(f"Dealer: {infoh_dealer}", False, self.TEXTCOLOR),
                    self.pokergame_ft.render(f"Player: {infoh_player}", False, self.TEXTCOLOR),
                    self.pokergame_ft.render(f"You lost {result} CR", False, self.TEXTCOLOR)
                ]

        else:
            raise ValueError('MatchOver event contains a non-valid value for attrib "won". Received value:', ev.won)

        # push to serv
        if result != 0:
            hackfromcli_side(result)

    @staticmethod
    def centerblit(refscr, surf, p):
        w, h = surf.get_size()
        refscr.blit(surf, (p[0] - w // 2, p[1] - h // 2))

    def on_paint(self, ev):
        if not self._assets_rdy:
            self._load_assets()
        refscr = ev.screen

        refscr.fill('darkgreen')
        # affiche mains du dealer +decor casino
        refscr.blit(self.bg, (0, 0))

        # - do this for any PokerState!
        refscr.blit(self.overlay_spr, OVERLAY_POS)

        # draw GUI labels...
        for etq in self._gui_labels.values():
            etq.draw()

        # draw ante, blind amounts, & the total cash
        for etq in self._mlabels.values():
            etq.draw()  # it has its pos inside the Label instance

        cardback = self._my_assets['card_back']

        # ---------- draw chip value if the phase is still "setante"
        if self._mod.stage == common.PokerStates.AnteSelection:

            self.adhoc_chip_spr.rect.center = PLAYER_CHIPS['2a']
            refscr.blit(self.adhoc_chip_spr.image, self.adhoc_chip_spr.rect.topleft)

            # -- debug chip img & dropzones {{
            if self.debug_drag_n_drop:
                pygame.draw.rect(refscr, 'red',
                                 (self.adhoc_chip_spr.rect.topleft, self.adhoc_chip_spr.image.get_size()), 1)
                for dzo in self._rect_dropzone_li:
                    pygame.draw.rect(refscr, 'orange', dzo, 1)
                for b in self._act_related_wcontainer.content:
                    refscr.blit(b.image, b.get_pos())
            # }}

            # draw the drag n drop Chip
            if self.dragged_chip_pos:
                UthView.centerblit(ev.screen, self.adhoc_chip_spr.image, self.dragged_chip_pos)

        else:
            # ----------------
            #  draw all cards
            # ----------------
            for loc in CARD_SLOTS_POS.keys():
                if self._mod.visibility[loc]:
                    desc = self._mod.get_card_code(loc)
                    x = self._my_assets[desc]
                else:
                    x = cardback
                UthView.centerblit(refscr, x, CARD_SLOTS_POS[loc])

        # display all 3 prompt messages
        offsety = 24
        if self.info_msg0:
            refscr.blit(self.info_msg0, STATUS_MSG_BASEPOS)
        if self.info_msg1:
            rank = 1
            refscr.blit(self.info_msg1, (STATUS_MSG_BASEPOS[0], STATUS_MSG_BASEPOS[1] + offsety * rank))
        else:
            if len(self.info_messages):
                for rank, e in enumerate(self.info_messages):
                    refscr.blit(e, (STATUS_MSG_BASEPOS[0], STATUS_MSG_BASEPOS[1] + offsety * (rank + 1)))

        self._chips_related_wcontainer.draw()
        # self._money_labels.draw()
        self._act_related_wcontainer.draw()
        self.generic_wcontainer.draw()  # will be drawn or no, depending on if its active!


# ---------------------------------------------------
#  post view
# ---------------------------------------------------

"""
Using pairs of (dedicated_controller, specific_gamestate)
is a nice way to ease state transition in this Poker game

Hence we define every game state in the most explicit manner, BUT we keep
the same model & the same view obj ALL ALONG, when transitioning...
"""


class AnteSelectionCtrl(pyv.EvListener):
    """
    selecting the amount to bet
    """

    def __init__(self, ref_m):
        super().__init__()
        self._mod = ref_m
        self.recent_date = None
        self.autoplay = False
        self._last_t = None

    def on_deal_cards(self, ev):
        self._mod.check()  # =>launch match
        self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.PreFlop)
        # useful ??
        self.recent_date = None
        self.autoplay = False
        self._last_t = None

    def on_cycle_chipval(self, ev):
        chval = self._mod.get_chipvalue()
        if ev.upwards:
            common.chip_scrollup(chval)
        else:
            common.chip_scrolldown(chval)

    def on_bet_undo(self, ev):
        pass  # TODO


class AnteSelectionState(pyv.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.c = None

    def enter(self):
        # ensure "manually" that the model has the right state
        common.refmodel._pokerstate = common.PokerStates.AnteSelection

        # force the reset of the view, bc if its not the 1st match played, its state can be "non-eden"
        # and thats not what we need
        common.refview.turn_off()

        common.refview = UthView(common.refmodel)
        common.refview.turn_on()

        print('[AnteSelectionState] enter!')
        common.refview.show_anteselection()
        self.c = AnteSelectionCtrl(common.refmodel)
        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        common.refview.hide_anteselection()
        print('[AnteSelectionState] release!')
        print()


# --------------------------------------------
class PreFlopCtrl(pyv.EvListener):
    """
    selecting the amount to bet
    """

    def __init__(self, ref_m):
        self.m = ref_m
        super().__init__()

    def _iter_gstate(self):
        self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.Flop)

    def on_check_decision(self, ev):
        self.m.check()
        self._iter_gstate()

    # what button has been clicked? The one with x4 or the one with x3?
    def on_bet_high_decision(self, ev):
        print('Impact x4')
        self.m.select_bet(bullish_choice=True)
        self._iter_gstate()

    def on_bet_decision(self, ev):
        print('Impact x3')
        self.m.select_bet()
        self._iter_gstate()


class PreFlopState(pyv.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.c = None

    def enter(self):
        common.refview.show_generic_gui()  # that part of Gui will stay active until bets are over
        self.c = PreFlopCtrl(common.refmodel)
        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        common.refview.hide_generic_gui()


class FlopCtrl(pyv.EvListener):
    """
    selecting the amount to bet
    """

    def __init__(self, ref_m, ):
        super().__init__()
        self.m = ref_m

    def _iter_gstate(self):
        self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.TurnRiver)

    def on_bet_decision(self, ev):
        # TODO what button has been clicked? The one with x4 or the one with x3?
        self.m.select_bet()
        self._iter_gstate()

    def on_check_decision(self, ev):
        self.m.check()
        self._iter_gstate()

    def on_mousedown(self, ev):
        if self.m.autoplay:
            print('Zap')
            self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.TurnRiver)
            self.m._goto_next_state()  # returns False if there's no next state


class FlopState(pyv.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.c = None

    def enter(self):
        if not common.refmodel.autoplay:
            common.refview.show_generic_gui()  # show it again!
            widgetc = common.refview.generic_wcontainer
            widgetc.bet_button.label = 'Bet x2'
            widgetc.bethigh_button.set_active(False)

        self.c = FlopCtrl(common.refmodel)
        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        common.refview.hide_generic_gui()


# --------------------------------------------
class TurnRiverCtrl(pyv.EvListener):
    """
    selecting the amount to bet
    """

    def __init__(self, ref_m, ref_v):
        super().__init__()
        self.m = ref_m

    def _iter_gstate(self):
        self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.Outcome)

    def on_mousedown(self, ev):
        if self.m.autoplay:
            self.m._goto_next_state()  # returns False if there's no next state
            self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.Outcome)

    def on_bet_decision(self, ev):
        self.m.select_bet()
        print('BET au TR')
        self._iter_gstate()

    def on_check_decision(self, ev):
        self.m.fold()
        print('un check au TR vaut pour Fold!!')
        self._iter_gstate()


class TurnRiverState(pyv.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.c = None

    def enter(self):
        if not common.refmodel.autoplay:
            common.refview.show_generic_gui()
            wcontainer = common.refview.generic_wcontainer
            wcontainer.bethigh_button.set_active(False)
            wcontainer.bet_button.label = 'Bet x1'
            wcontainer.check_button.label = 'Fold'

        self.c = TurnRiverCtrl(common.refmodel, None)
        self.c.turn_on()

    def release(self):
        common.refview.hide_generic_gui()
        print(' LEAVE turn-river st.')
        self.c.turn_off()


class OutcomeCtrl(pyv.EvListener):
    def __init__(self, ref_m):
        super().__init__()
        self._mod = ref_m

    def on_mousedown(self, ev):
        if self._mod.match_over:
            self.pev(pyv.EngineEvTypes.StateChange, state_ident=common.PokerStates.AnteSelection)

            # COLLECT what was won
            self._mod.wallet.collect_case_victory()

            # force the new round!
            self._mod.init_new_round()


class OutcomeState(pyv.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.c = None

    def enter(self):
        self.c = OutcomeCtrl(common.refmodel)
        self.c.turn_on()

    def release(self):
        self.c.turn_off()


class ErrMsgView(pyv.EvListener):
    def on_paint(self, ev):
        ev.screen.fill('darkgreen')
        if not hasattr(self, 'caption'):
            tmpft = pygame.font.Font(None, 24)
            tmpftB = pygame.font.Font(None, 16)
            self.caption0 = tmpft.render('To play this game you need an account', None, 'orange')
            self.caption1 = tmpftB.render('Please go back to the hypergame (press ESC)', None, 'gray')
            self.caption2 = tmpftB.render(
                'Use a terminal, and use the "fauth" command. Ask on Discord if you need help.', None, 'gray')

        ev.screen.blit(self.caption0, (33, 100))
        ev.screen.blit(self.caption1, (33, 200))
        ev.screen.blit(self.caption2, (33, 235))


class PokerUth(pyv.GameTpl):
    def __init__(self):
        super().__init__()
        self.m = self.v = None

    def get_video_mode(self):
        return 1

    def list_game_events(self):
        return common.MyEvTypes

    def enter(self, vms=None):
        super().enter(vms)

        pyv.init()
        pyv.create_screen()
        pyv.vars.clock = pyv.create_clock()

        # ----------- ajout forced auth -----------
        # c = katasdk.get_pyconnector()
        # if not c.is_logged:
        #    self.v = ErrMsgView()
        #    self.v.turn_on()
        if False:
            pass
        else:
            pyv.declare_game_states(
                common.PokerStates,
                {
                    common.PokerStates.AnteSelection: AnteSelectionState,
                    common.PokerStates.PreFlop: PreFlopState,
                    common.PokerStates.Flop: FlopState,
                    common.PokerStates.TurnRiver: TurnRiverState,
                    common.PokerStates.Outcome: OutcomeState
                },
                self
            )
            self.m = UthModel()
            common.refmodel = self.m
            self.v = UthView(self.m)
            common.refview = self.v
            self.v.turn_on()


game_obj = PokerUth()
game_obj.loop()

# katasdk.gkart_activation(game_obj)
