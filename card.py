# Simple class representing a card
class Card:
    # Some Class-level constants for human readability of code
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3

    JACK =  9
    QUEEN = 10
    KING = 11
    ACE = 12
    
    suits = ['S', 'H', 'C', 'D']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank
        self.sort_key = self.suit*13 + self.rank

    # secondary constructor to handle the 'AD' (for Ace of Diamonds)
    # type of argument.
    @classmethod
    def create(cls, string):
        assert len(string) == 2
        rank = Card.ranks.index(string[0])
        suit = Card.suits.index(string[1])
        card = cls(rank, suit)
        return card

    def __eq__(self, other):
        if other is None:
            return False
        if (self.suit == other.suit) and (self.rank == other.rank):
            return True
        return False


    def __gt__(self, other):
        if other is None:
            return False
        if self.suit == other.suit:
            return self.rank > other.rank
        if self.suit == Card.SPADES:
            return True
        return False

    def __lt__(self, other):
        if other is None:
            return False
        if self.suit == other.suit:
            return self.rank < other.rank
        return False
    
    def __hash__(self):
        return hash((self.suit, self.rank))
    
    def __repr__(self):
        return "{0}{1}".format(Card.ranks[self.rank], Card.suits[self.suit])

    def __str__(self):
        return "{0}{1}".format(Card.ranks[self.rank], Card.suits[self.suit])

