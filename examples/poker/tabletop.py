import operator
import random

import katagames_engine as kengi


# - constants
CARD_SIZE_PX = (82, 120)


class PokerHand:
    """
    From highest to lowest
    > Royal flush: A, K, Q, J, 10, all the same suit
    > Straight flush: Five cards in a sequence, all in the same suit
    > Four of a kind: All four cards of the same rank
    > Full house: Three of a kind with a pair
    > Flush: Any five cards of the same suit, but not in a sequence
    > Straight: Five cards in a sequence, but not of the same suit
    > Three of a kind: Three cards of the same rank
    > Two pair: Two different pairs
    > One Pair: Two cards of the same rank
    > High card: When you haven't made any of the hands above
    """

    def __init__(self, hand):
        self.hand = hand  # list of cards

    def __str__(self):
        out = ""
        for card in self.hand:
            out += str(card) + ", "
        return out

    def __getitem__(self, index):
        return self.hand[index]

    def __len__(self):
        return len(self.hand)

    def is_straight(self):
        """
        a hand is a straight if, when sorted, the current card's rank + 1 is the same as the next card
        """
        values = list()
        for card in self.hand:
            values.append(int(PokerHand.adhoc_mapping(card.rank)))
        values.sort()

        for n in range(0, 4):
            if values[n] + 1 != values[n+1]:
                return False
        return True

    def is_flush(self):
        """a hand is a flush if all the cards are of the same suit
        """
        for suit in StdCard.OMEGA_SUIT:
            # - debug by tom
            # print(f'test [{suit}]')
            # print(f'  [{self.hand[0].suit}]')
            # print(f'  [{self.hand[1].suit}]')
            # print(f'  [{self.hand[2].suit}]')
            # print(f'  [{self.hand[3].suit}]')
            # print(f'  [{self.hand[4].suit}]')
            if all((
                suit == self.hand[0].suit,
                suit == self.hand[1].suit,
                suit == self.hand[2].suit,
                suit == self.hand[3].suit,
                suit == self.hand[4].suit
            )):
                return True
        return False

    @staticmethod
    def adhoc_mapping(xx):
        tmp = {
            'T': 10,
            'J': 11,
            'Q': 12,
            'K': 13,
            'A': 14
        }
        if xx in tmp:
            rez = str(tmp[xx])
        else:
            rez = xx.zfill(2)
        return rez

    @property
    def score(self):
        """
        The first digits represents the type of hand and the rest represent the cards in the hands
        returns an integer that represents a score given to the hand.
        """
        card_count = dict()  # the count of each card rank (we ignore the suit for now)
        for tsym in StdCard.OMEGA_SYM:
            card_count[tsym] = 0

        for card in self.hand:
            x = card.code[0]
            card_count[x] += 1

        # count number of unique cards
        unique_count = 0
        for rankCount in card_count.values():
            if rankCount > 0:
                unique_count += 1

        straight = self.is_straight()
        flush = self.is_flush()
        points = 0

        if straight and flush:
            points = max(points, 9)  # straight flush
        elif flush and not straight:
            points = max(points, 6)  # flush
        elif not flush and straight:
            points = max(points, 5)  # straight

        elif unique_count == 2:
            if max(card_count.values()) == 4:
                points = 8  # four of a kind (2 uniques and 4 are the same)
            elif max(card_count.values()) == 3:
                points = 7  # full house (2 unique and 3 are the same)

        elif unique_count == 3:
            if max(card_count.values()) == 3:
                points = 4  # three of a kind (3 unique and 3 are the same)
            elif max(card_count.values()) == 2:
                points = 3  # two pair (3 uniques and 2 are the same)

        elif unique_count == 4:
            if max(card_count.values()) == 2:
                points = 2  # one pair (4 uniques and 2 are the same)

        elif unique_count == 5:
            points = 1  # high card

        # print out the values of the cards in order from greatest to least with 2 digits for each card
        # in order to generate a point value
        sorted_card_count = sorted(list(card_count.items()), key=operator.itemgetter(1, 0), reverse=True)
        for keyval in sorted_card_count:
            if keyval[1] != 0:
                points = int(str(points) + str(keyval[1] * PokerHand.adhoc_mapping(keyval[0])))
        return points


class StdCard:
    OMEGA_SYM = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')
    OMEGA_SUIT = ('c', 'd', 'h', 's')

    def __init__(self, code):
        if (not isinstance(code, str)) or len(code) != 2:
            raise ValueError('please pass a StdCard code to the constructor! Err1')
        sym, suit = code
        if suit not in self.OMEGA_SUIT:
            raise ValueError('StdCard code isnt valid! Err2(suit)')
        if sym not in self.OMEGA_SYM:
            raise ValueError('StdCard code isnt valid! Err3(sym)')
        self._code = code

    @classmethod
    def all_card_codes(cls):
        res = list()
        for sym in cls.OMEGA_SYM:
            for suit in cls.OMEGA_SUIT:
                res.append(sym + suit)
        return res

    @classmethod
    def draw_card(cls, excluded_set=None):
        if excluded_set is None:
            excluded_set = set()
        if len(excluded_set) >= 52:
            raise ValueError('draw_card Err: excluded_set is too broad!')
        omega_code0 = set(cls.all_card_codes())
        omega_code = tuple(omega_code0 - excluded_set)
        return cls(random.choice(omega_code))

    @property
    def code(self):
        return self._code

    @property
    def rank(self):
        return self._code[0]

    @property
    def rank_text(self):
        x = self._code[0]

        if x == 'J':
            return 'Jack'
        elif x == 'Q':
            return 'Queen'
        elif x == 'K':
            return 'King'
        elif x == 'A':
            return 'Ace'
        return {
            '2': 'Deuce',
            '3': 'Trey',
            '4': 'Four',
            '5': 'Five',
            '6': 'Six',
            '7': 'Seven',
            '8': 'Eight',
            '9': 'Nine',
            'T': 'Ten'
        }[x]

    @property
    def suit(self):
        return self._code[1]

    @property
    def suit_text(self):
        return {
            'c': 'Clubs',
            'd': 'Diamonds',
            'h': 'Hearts',
            's': 'Spades'
        }[self._code[1]]

    def __str__(self):
        return self.rank_text + ' of ' + self.suit_text


class CardDeck:

    def shuffle(self):
        random.shuffle(self.contenu)

    def __init__(self, contenu_init=None):
        """ Creates a default deck which contains all 52 cards and returns it. """

        if contenu_init is None:
            contenu = ['sj', 'sq', 'sk', 'sa']  # spades
            contenu.extend(['hj', 'hq', 'hk', 'ha'])  # hearts
            contenu.extend(['cj', 'cq', 'ck', 'ca'])  # clubs
            contenu.extend(['dj', 'dq', 'dk', 'da'])  # diamonds
            values = range(2, 11)
            for x in values:
                spades = "s" + str(x)
                hearts = "h" + str(x)
                clubs = "c" + str(x)
                diamonds = "d" + str(x)
                contenu.append(spades)
                contenu.append(hearts)
                contenu.append(clubs)
                contenu.append(diamonds)
            self.contenu = contenu
        else:
            self.contenu = contenu_init

    # anciennement def returnFromDead(self, deadDeck):
    def recois(self, autre_deck):
        """ Appends the cards from the deadDeck to the deck that is in play. This is called when the main deck
        has been emptied. """
        # équivaut à défausser deadDeck dans le paquet courant

        for card in autre_deck.contenu:
            self.contenu.append(card)
        self.shuffle()

        return self.__class__([])

    @property
    def size(self):
        return len(self.contenu)

    def get_info_card(self, ind):
        return self.contenu[ind]

    def deck_deal(self, dead_deck):
        """
        Shuffles the deck, takes the top 4 cards off the deck,
        appends them to the player's and dealer's hands, and
        returns the player's and dealer's hands.
        """
        self.shuffle()

        li_dealer_hand, li_player_hand = [], []
        cards_to_deal = 4
        deck = self.contenu
        while cards_to_deal > 0:
            if len(deck) == 0:
                dead_deck = self.recois(dead_deck)

            # deal the first card to the player, second to dealer, 3rd to player, 4th to dealer, based on divisibility
            # (it starts at 4, so it's even first)
            if cards_to_deal % 2 == 0:
                li_player_hand.append(deck[0])
            else:
                li_dealer_hand.append(deck[0])

            del deck[0]
            cards_to_deal -= 1
        cls = self.__class__
        return dead_deck, cls(li_player_hand), cls(li_dealer_hand)

    def hit(self, dealt_deck, hand):
        """ Checks to see if the deck is gone, in which case it takes the cards from
        the dead deck (cards that have been played and discarded)
        and shuffles them in. Then if the player is hitting, it gives
        a card to the player, or if the dealer is hitting, gives one to the dealer."""

        # if the deck is empty, shuffle in the dead deck
        deck = self.contenu
        if len(deck) == 0:
            dealt_deck = self.recois(dealt_deck)

        hand.contenu.append(deck[0])
        del deck[0]
        return dealt_deck, hand

    @classmethod
    def bj_value(cls, hand):
        """ Checks the value of the cards in the player's or dealer's hand. """
        total_value = 0

        for card in hand.contenu:
            value = card[1:]

            # Jacks, kings and queens are all worth 10, and ace is worth 11    
            if value == 'j' or value == 'q' or value == 'k':
                value = 10
            elif value == 'a':
                value = 11
            else:
                value = int(value)

            total_value += value

        if total_value > 21:
            for card in hand.contenu:
                # If the player would bust and he has an ace in his hand, the ace's value is diminished by 10    
                # In situations where there are multiple aces in the hand, this checks to see if the total value
                # would still be over 21 if the second ace wasn't changed to a value of one.
                # if it's under 21, there's no need
                # to change the value of the second ace, so the loop breaks. 
                if card[1] == 'a':
                    total_value -= 10
                if total_value <= 21:
                    break
        return total_value


def _init_and_tests():
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


"""
----------------------------------------------
   W.i.p. <> below I perform some tests legacy classes/
   chunks copied from elsewhere still need to be merged/unified
----------------------------------------------- 
"""

if __name__ == '__main__':
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
    kengi.bootstrap_e()
    kengi.init('custom', screen_dim=(1920, 1080))
    pygame = kengi.pygame

    # -------load assets---
    cardBack = pygame.image.load('img/back.png').convert_alpha()
    cardBack = pygame.transform.scale(cardBack, (CARD_SIZE_PX[0], CARD_SIZE_PX[1]))

    images = dict()
    for card_cod in StdCard.all_card_codes():
        # converting card code to path
        y = PokerHand.adhoc_mapping(card_cod[0]).lstrip('0') + card_cod[1].upper()
        img_path = f'img/{y}.png'
        images[card_cod] = pygame.image.load(img_path).convert_alpha()
        images[card_cod] = pygame.transform.scale(images[card_cod], CARD_SIZE_PX)

    # {{{{ mini-tutorial, then the game loop }}}}
    print()
    print('using the program:')
    print('  PRESS SPACE to test the PokerHand instance update...')
    print('  ESCAPE to quit')
    print()

    gameover = False
    screen = kengi.get_surface()
    bg = pygame.image.load('img/bg0.jpg')
    while not gameover:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                gameover = True
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                gameover = True
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                alea_xx = PokerHand([StdCard.draw_card() for _ in range(5)])  # not from a deck -> raw 1/52 chance
                # TODO blit the type of hand (Two pair, Full house etc) + the score val.

        # refresh gfx
        screen.blit(bg, (0, 0))
        for i in range(5):
            screen.blit(images[alea_xx[i].code], (25 + 110*i, 10))
        for i in range(5):
            screen.blit(images[lambda_hand[i].code], (25 + 110*i, 158))
        for i in range(5):
            screen.blit(images[epic_hand[i].code], (25 + 110*i, 296))
        kengi.flip()

    print('bye!')
