import math
import random
import operator

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

# Class representing the Player
class Player:
    # AGENT API FUNCTION __init__(self)
    #
    # An __init__ method that takes to arguments to instantiate the class.
    # TO DO: Remove ID argument. Since I'm playing 4 copies of the same agent
    #        against each other, I use the ID to refer to them. Need to rework
    #        to a name based method.
    #
    def __init__(self, name):
        self.playerID = -1
        self.name = name
        # list of all cards in your hand
        self._hand = []

    # AGENT API FUNCTION get_name(self)
    #
    # Returns a string of the agent's name. The design seems aimed at having 4
    # agent's, each with a different hard coded name.
    #
    def get_name(self):
        return self.name

    # AGENT API FUNCTION get_hand(self)
    #
    # Returns a list of two character strings representing cards in the agent's hand
    #
    def get_hand(self):
        return [str(c) for c in self._hand.sort(key=sort.key)]

    # AGENT API FUNCTION new_hand(self, names)
    #
    # Takes a list of names of all agents in the game in clockwise order
    # and returns nothing. This method is also responsible for clearing any data
    # necessary for your agent to start a new round.
    #
    def new_hand(self, names):
        self.__players = names
        self.playerID = names.index(self.get_name())
        self._hand = []
    
    # AGENT API FUNCTION add_cards_to_hand(self, cards)
    #
    # A method that takes a single argument, a list of two character strings representing cards to be
    # added to the agent's hand. This is used for dealing and psssing and so should be able to take a
    # list of length of any length. This method should return nothing
    #
    def add_cards_to_hand(self, cards):
        for c in cards:
            assert(len(c) == 2)
            rank = Card.ranks.index(c[0])
            suit = Card.suits.index(c[1])
            card = Card(rank, suit)
            self._hand.append(card)
        
    # AGENT API FUNCTION play_card(self, lead, trick)
    #
    # This will likely be the bulk of your code. This method takes two
    # arguments, the name of the player who is leading the trick, and a
    # list of two character strings of the cards that have been played
    # so far this trick. This method should return a single two character
    # string representing the card your agent has chosen to play. From
    # this method your agent should also track which cards are left in
    # its hand.
    #
    def play_card(self, lead, trick):

        def drop_card(rank, suit):
            # since you're playing this card, remove it from your hand
            print("{0} played {1} from hand {2}".format(self.name, Card(rank, suit), self._hand))
            self._hand.remove(Card(rank, suit))
            return Card.ranks[rank] + Card.suits[suit]

        def pick_a_card_to_lead_with():
            return random.choice(self._hand)


        def pick_a_card_to_follow_suit(suit_led):
            cards_in_suit = [c for c in self._hand if c.suit == suit_led]
            return random.choice(cards_in_suit)


        def pick_a_non_led_card_to_discard():
            return random.choice(self._hand)

        
        # If no cards in the trick so far, it's the first time so you get to pick any card
        if len(trick) == 0:
            card = pick_a_card_to_lead_with()
            suit_led = card.suit
            return drop_card(card.rank, card.suit)
        else:
            # else, if you can follow suit, you must follow suit
            suit_led = Card.create(trick[0]).suit
            cards_in_suit = [c for c in self._hand if c.suit == suit_led]
            if len(cards_in_suit) > 0:
                card = pick_a_card_to_follow_suit(suit_led)
                return drop_card(card.rank, card.suit)
            # finally, if you don't have a card in the suit, you must still pick a card
            # (hopefully a losing card) from one of the other suits to discard
            else:
                card = pick_a_non_led_card_to_discard()
                return drop_card(card.rank, card.suit)
    # AGENT API FUNCTION: collect_trick(self, lead, winner, trick)
    #
    # Takes 3 arguments. A string of the name of the player who led the trick, a string of the name of
    # the player who won the trick, and a list of the twi character strings representing the card in the
    # trick in the order they were played, starting with the lead.
    #
    def collect_trick(self, lead, winner, trick):
        # if you're the winner of the trick, increment the number of tricks taken
        if self.name == winner:
            self.__trick_taken += 1
        
    # AGENT API FUNCTION: score(self)
    #
    # Takes no arguments and returns an integer of the number of point your agent scored on this hand.
    #
    def score(self):
        return self.__trick_taken


class Organic_Chem_Survivors_Agent(Player):
    def __init__(self):
        Player.__init__(self, "Organic Chem Survivors")
