import operator
import random


class Card:
	def __init__(self, rank, suit):

		self.rank = 0
		self.suit = ''
		self.image_path = ('img/' + str(rank) + str(suit) + '.png')
		self.selected = False

		# convert the rank to an integer so it's easier to compute the winner of a hand
		if rank == 'A':
			self.rank = 14
		elif rank == 'K':
			self.rank = 13
		elif rank == 'Q':
			self.rank = 12
		elif rank == 'J':
			self.rank = 11
		elif rank == 'T':
			self.rank = 10
		else:
			self.rank = int(rank)

		self.suit = suit

	def __str__(self):
		out = ""

		# convert rank back to a word so it's easier to read
		if self.rank == 14:
			out += "Ace"
		elif self.rank == 13:
			out += "King"
		elif self.rank == 12:
			out += "Queen"
		elif self.rank == 11:
			out += "Jack"
		else:
			out += str(self.rank)

		out += ' of '

		# convert the suit to a word so it's easier to read
		if self.suit == 'H':
			out += 'Hearts'
		elif self.suit == 'S':
			out += 'Spades'
		elif self.suit == 'C':
			out += 'Clubs'
		else:
			out += 'Diamonds'

		return out


# only exists for the __str__ function
class Hand:

	def __init__(self, hand):
		self.hand = hand

	def __str__(self):
		out = ""
		for card in self.hand:
			out += str(card) + ", "
		return out

	def __getitem__(self, index):
		return self.hand[index]

	def __len__(self):
		return len(self.hand)


class Deck:

	def __init__(self):
		self.deck = []

		for suit in ['H', 'S', 'C', 'D']:
			for rank in range(2, 15):
				self.deck.append(Card(rank, suit))

	def __str__(self):
		out = ""
		for card in self.deck:
			out += str(card) + "\n"
		return out

	def __getitem__(self, index):
		return self.deck[index]

	# return a list a cards taken from the deck
	def deal(self, amount):
		cards = []

		# cap out the cards dealt
		if amount > len(self.deck):
			print("There are not enough cards!  I can only deal " + str(len(self.deck)) + " cards.")
			amount = len(self.deck)

		# create and then return a list of cards taken randomly from the deck
		for i in range(amount):
			card = random.choice(self.deck)
			self.deck.remove(card)
			cards.append(card)
		return cards


class Poker:

	def __init__(self, scores=None):
		self.deck = Deck()
		if scores is None:
			self.scores = [0, 0, 0, 0]
		else:
			self.scores = scores

		self.playerHand = Hand(self.deck.deal(5))
		self.comp1Hand = Hand(self.deck.deal(5))
		self.comp2Hand = Hand(self.deck.deal(5))
		self.comp3Hand = Hand(self.deck.deal(5))

	def computer_replace(self):
		# make each computer take a turn
		self.AI_replace(self.comp1Hand)
		self.AI_replace(self.comp2Hand)
		self.AI_replace(self.comp3Hand)

	def get_most_suit(self, hand):
		suits = {'H': 0, 'C': 0, 'S': 0, 'D': 0}
		for card in hand:
			suits[card.suit] += 1
		return max(list(suits.items()), key=operator.itemgetter(1))[0]

	def get_most_rank(self, hand):
		ranks = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}
		for card in hand:
			ranks[card.rank] += 1
		return max(list(ranks.items()), key=operator.itemgetter(1))[0]

	def replace_suit(self, hand):
		suit = self.get_most_suit(hand)
		for card in hand:
			if card.suit != suit:
				card.selected = True
		self.replace(hand)

	def replace_rank(self, hand):
		rank = self.get_most_rank(hand)
		for card in hand:
			if card.rank != rank:
				card.selected = True
		self.replace(hand)

	def AI_replace(self, hand):
		score = self.get_score(hand)
		# decide which cards not to toss away so as to keep the same score
		if str(score)[0] == '1':  # High card, try for flush
			self.replace_suit(hand)
		elif str(score)[0] == '2':  # One pair, switch out cards not paired
			self.replace_rank(hand)
		elif str(score)[0] == '3':  # Two pair, switch out card not paired
			self.replace_rank(hand)
		elif str(score)[0] == '4':  # Three of a kind, switch out cards not paired
			self.replace_rank(hand)
		elif str(score)[0] == '8':  # Four of a kind, switch out the not paired not
			self.replace_rank(hand)
	# all other cases are a pass

	def replace(self, hand):
		# replaces the selected cards in the hand with the top cards on the deck
		count = 0
		for i in range(3):
			for card in hand:
				if card.selected:
					hand.hand.remove(card)
					count += 1

		hand.hand.extend(self.deck.deal(count))

	def play_round(self):
		"""plays a round of poker with 4 hands
		# winner is displayed and scores for each hand as well
		# the number of the winner is returned by the function
		"""
		score1 = self.get_score(self.playerHand)
		score2 = self.get_score(self.comp1Hand)
		score3 = self.get_score(self.comp2Hand)
		score4 = self.get_score(self.comp3Hand)

		winner = max(score1, max(score2, max(score3, score4)))

		if winner == score1:
			self.scores[0] += 1

		elif winner == score2:
			self.scores[1] += 1

		elif winner == score3:
			self.scores[2] += 1

		elif winner == score4:
			self.scores[3] += 1

		return [score1, score2, score3, score4]

	def get_score(self, hand):
		"""
		The first digits represents the type of hand and the rest represent the cards in the hands
		returns an integer that represents a score given to the hand.
		"""
		hand = self
		# make a dictionary containing the count of each each
		card_count = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}

		for card in hand.hand:
			card_count[card.rank] += 1

		# count number of unique cards
		unique_count = 0
		for rankCount in card_count.values():
			if rankCount > 0:
				unique_count += 1

		straight = Poker.is_straight(hand)
		flush = Poker.is_flush(hand)

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
				points = int(str(points) + (keyval[1] * str(keyval[0]).zfill(2)))

		return points

	@staticmethod
	def convert_score(score):
		"""given an integer score, returns the poker term equivalent
		"""
		if str(score)[0] == '1':
			return "High Card"
		elif str(score)[0] == '2':
			return "One Pair"
		elif str(score)[0] == '3':
			return "Two Pair"
		elif str(score)[0] == '4':
			return "Three of a Kind"
		elif str(score)[0] == '5':
			return "Straight"
		elif str(score)[0] == '6':
			return "Flush"
		elif str(score)[0] == '7':
			return "Full House"
		elif str(score)[0] == '8':
			return "Four of a Kind"
		elif str(score)[0] == '9':
			return "Straight Flush"

	@staticmethod
	def is_straight(hand):
		"""
		a hand is a straight if, when sorted, the current card's rank + 1 is the same as the next card
		"""
		values = []
		for card in hand.hand:
			values.append(card.rank)

		values.sort()

		for i in range(0, 4):
			if values[i] + 1 != values[i + 1]:
				return False
		return True

	@staticmethod
	def is_flush(hand):
		"""a hand is a flush if all the cards are of the same suit
		"""
		suit = hand.hand[0].suit
		for card in hand.hand:
			if card.suit != suit:
				return False
		return True
