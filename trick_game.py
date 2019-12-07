import argparse
from enum import IntEnum
import importlib
import random

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('player_file', help='.py filename of the agent player class')

    return parser.parse_known_args()

class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.playing_order = []
        self.tricks = {}
        self._score = 0

    def get_name(self):
        return self.name

    def get_hand(self):
        return self.hand

    def new_hand(self, names):
        self.playing_order = names
        for name in names:
            self.tricks[name] = []
        self.hand = []

    def add_cards_to_hand(self, cards):
        self.hand += cards

    def collect_trick(self, lead, winner, trick):
        self.tricks[winner].append(trick)

    def score(self):
        score = len(self.tricks[self.name])
        self._score += score

        return score

    def play_card(self, lead, trick):
        # if lead play random card
        if lead == self.name:
            return self.hand.pop(random.randint(0, len(self.hand) - 1))
        # follow suit if possible
        else:
            lead_suit = trick[0][-1]
            playable_cards = [card for card in self.hand if card[-1] == lead_suit]
            if playable_cards:
                return self.hand.pop(self.hand.index(random.choice(playable_cards)))

        # Can't follow suit so play random card
        return self.hand.pop(random.randint(0, len(self.hand) - 1))

class Suit(IntEnum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._label = label

        return obj

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'

    @property
    def label(self):
        return self._label

    SPADES = (1, 'S')
    HEARTS = (2, 'H')
    DIAMONDS = (3, 'D')
    CLUBS = (4, 'C')

class Rank(IntEnum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._label = label

        return obj

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'

    @property
    def label(self):
        return self._label

    TWO = (1, '2')
    THREE = (2, '3')
    FOUR = (3, '4')
    FIVE = (4, '5')
    SIX = (5, '6')
    SEVEN = (6, '7')
    EIGHT = (7, '8')
    NINE = (8, '9')
    TEN = (9, 'T')
    JACK = (10, 'J')
    QUEEN = (11, 'Q')
    KING = (12, 'K')
    ACE = (13, 'A')

class Deck(object):
    def __init__(self):
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]

    @property
    def size(self):
        return len(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)

    def deal(self, n=1):
        return [self._cards.pop() for _ in range(n)]

class Card(object):
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    @classmethod
    def from_name(cls, name):
        for rank in Rank:
            if rank.label == name[:-1]:
                r = rank
        for suit in Suit:
            if suit.label == name[-1]:
                s = suit

        return Card(r, s)

    def __repr__(self):
        return f'Card({self._rank.label}, {self._suit.label})'

    def __str__(self):
        return f'{self._rank.label}{self._suit.label}'

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    @property
    def name(self):
        return self.rank.label + self.suit.label

    @property
    def rank(self):
        return self._rank

    @property
    def suit(self):
        return self._suit

def card_compare(card1, card2):
    """
    Compares cards two cards in a trick to see which one is greater.
    One of the cards will always be trump since trump is who led
    :param card1 Card:
    :param card2 Card:
    :return: 1 if card1 greater, -1 if card2 greater, 0 if same
    """
    if card2.suit is card1.suit and card2.rank > card1.rank:
        return 1

    return -1

def resolve_trick(trick):
    win = trick[0]
    for card in trick:
        if card_compare(win, card) == 1:
            win = card

    return trick.index(win)

class Game(object):
    def __init__(self, agent):
        self._players = [
            agent,
            Player('Leonardo'),
            Player('Donatello'),
            Player('Rafael')
        ]

        random.shuffle(self._players)

        self._scores = {
            self._players[0].get_name(): 0,
            self._players[1].get_name(): 0,
            self._players[2].get_name(): 0,
            self._players[3].get_name(): 0,
        }

    @property
    def scores(self):
        return self._scores

    def play_game(self):
        hand_num = 0
        while max(list(self.scores.values())) < 100:
            for player in self._players:
                player.new_hand([player.get_name() for player in self._players])

            deck = Deck()
            deck.shuffle()
            for player in self._players:
                player.add_cards_to_hand([card.name for card in deck.deal(13)])

            lead = hand_num % 4

            print(f'New Hand! {self._players[lead].get_name()} starts!')
            for player in self._players:
                print(f'{player.get_name()}:\t{player.get_hand()}')

            for _ in range(13):
                trick = []
                for i in range(4):
                    current_player = self._players[(lead + i) % 4]
                    played_card = current_player.play_card(self._players[lead].get_name(), [card.name for card in trick])
                    #print(f'{current_player.get_name()}: {played_card}')
                    trick.append(Card.from_name(played_card))

                winner = (lead + resolve_trick(trick)) % 4

                for player in self._players:
                    player.collect_trick(
                        self._players[lead].get_name(),
                        self._players[winner].get_name(),
                        [card.name for card in trick]
                    )

                print(f'\nLead: {self._players[lead].get_name()}')
                print(f'Winner: {self._players[winner].get_name()}')
                print(f'[{trick[0]}, {trick[1]}, {trick[2]}, {trick[3]}]')

                lead = winner

            scores = [player.score() for player in self._players]
            print('\nHand over')
            for player in self._players:
                print(f'\t{player.get_name()}: {player.score()}')
                self._scores[player.get_name()] += player.score()

            print(f'Game scores: {self._scores}')
            print('*****')

            hand_num += 1

        print(f'Game Over! {max(self._scores, key=self._scores.get)} wins!\n')
        print(f'Final Scores')
        print('------------')
        for player, score in self._scores.items():
            print(f'\t{player}: {score}')

if __name__ == '__main__':
    ARGS, unused = parse_args()

    agent_module = importlib.import_module(ARGS.player_file, '.')
    game = Game(agent_module.Player())
    game.play_game()
