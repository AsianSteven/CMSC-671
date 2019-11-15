import random
from card import Card

# A simple class representing an entire deck of playing cards. Simply
# creates the deck of 52 cards and has a procedure to randomly shuffle them.
class Deck:
    def __init__(self):
        self.deck = []
        for suit in range(len(Card.suits)):
            for rank in range(len(Card.ranks)):
                self.deck.append(Card(rank, suit))
    def shuffle(self):
        random.shuffle(self.deck)
