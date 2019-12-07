import math
import random
import operator
import numpy

import math
import random
import operator
import numpy

# Simple class representing a card
class OCSCard:
    # Some Class-level constants for human readability of code
    NR_SUITS = 4
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
        rank = OCSCard.ranks.index(string[0])
        suit = OCSCard.suits.index(string[1])
        card = cls(rank, suit)
        return card

    def __eq__(self, other):
        if other is None:
            return None
        if (self.suit == other.suit) and (self.rank == other.rank):
            return True
        return False


    def __gt__(self, other):
        if other is None:
            return None
        if self.suit == other.suit:
            return self.rank > other.rank
##        if self.suit == OCSCard.SPADES:
##            return True
        return False

    def __lt__(self, other):
        if other is None:
            return None
        if self.suit == other.suit:
            return self.rank < other.rank
        return False
    
    def __hash__(self):
        return hash((self.sort_key, self.suit, self.rank))
    
    def __repr__(self):
        return "{0}{1}".format(OCSCard.ranks[self.rank], OCSCard.suits[self.suit])

    def __str__(self):
        return "{0}{1}".format(OCSCard.ranks[self.rank], OCSCard.suits[self.suit])

# A simple class representing an entire deck of playing cards. Simply
# creates the deck of 52 cards and has a procedure to randomly shuffle them.
class Deck:
    def __init__(self):
        self.deck = []
        for suit in range(len(OCSCard.suits)):
            for rank in range(len(OCSCard.ranks)):
                self.deck.append(OCSCard(rank, suit))
    def shuffle(self):
        random.shuffle(self.deck)

# The state object represents the agent's knowledge about the state of the game. It includes
# some information about what's in your hand, what cards haven't been seen yet, which players
# are out of a suit, a guess-timate of the number of "full rounds" remaining that assumes a
# uniform distribution of outstanding cards, cards that are expected to win tricks and cards
# expected to lose tricks. The state is recalculated at the beginning of each call to play_card
# to give the agent the most current information
class State(object):
    def __init__(self, hand, unseen_cards):
        self._hand = hand
        self._unseen_cards = unseen_cards
        # list of all cards that the agent hasn't seen (either in its own hand or played in a trick)
        # the cards in your hand broken down by suit (and ordered by rank)
        self._cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        self._card_count = [0, 0, 0, 0]
        # the unseen cards broken down by suit (and ordered by rank)
        self._outstanding_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        self._outstanding_card_count = [0, 0, 0, 0]
        # maximum number of full rounds that could be played by suit if the outstanding cards are
        # uniformly distributed
        self._potential_full_rounds = [0, 0, 0, 0]
        self._cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        self._card_count = [0, 0, 0, 0]
        self._outstanding_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        self._outstanding_card_count = [0, 0, 0, 0]
        # called "potential" winners instead of guaranteed winners in anticipation of trumps being
        # introduced into the game...
        self._potential_winners = [ [], [], [], [] ]
        self._non_winners = [ [], [], [], [] ]
        for card in self._hand:
            self._cards[card.suit].append(card.rank)
        for card in self._unseen_cards:
            rank = OCSCard.ranks.index(card[0])
            suit = OCSCard.suits.index(card[1])
            self._outstanding_cards[suit].append(rank)
        for suit in range(OCSCard.NR_SUITS):
            self._cards[suit].sort()
            self._card_count[suit] = len(self._cards[suit])
            self._outstanding_cards[suit].sort()
            self._outstanding_card_count[suit] = len(self._outstanding_cards[suit])
            if self._card_count[suit] > 0:
                for j in range(self._card_count[suit]):
                    if self._outstanding_card_count[suit] == 0:
                        # there are no outstanding cards in this suit, so in the absence of trump these are winners
                        self._potential_winners[suit].append(self._cards[suit][j])
                    elif self._cards[suit][j] > self._outstanding_cards[suit][-1]:
                        # cards greater than the highest outstanding suit
                        self._potential_winners[suit].append(self._cards[suit][j])
                    else:
                        # these cards could be beaten by another player at this point, so they shouldn't be used
                        # as leads if you expect to win...viewing all of the opponents as cutthroat players
                        self._non_winners[suit].append(self._cards[suit][j])

        # The maximum number of full rounds possible assuming a uniform distribution of outstanding cards
        # is just the number of outstanding cards divided by 3 and rounded down. There is, of course, no
        # guarantee the cards are uniformly distributed. In fact, it's unlikely. This is just used as a
        # simple heuristic to decide whether or not a card has potential as a winner
        self._potential_full_rounds = [math.floor(x/3) for x in self._outstanding_card_count]

          
# Class representing the Player
class BasePlayer(object):
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
        # tracks all cards the agent has not "seen" either in it's own hand or played in a trick
        self._unseen_cards = []
        self.state = None
        self._tricks_won = 0
        # flag to indicate when a particular player is known to be out of a particular suit
        # useful anytime as it hints at the distribution of cards, but will be particularly useful
        # when trumps are introduced...
        self._player_out_of_suit = {
            0: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            1: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            2: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            3: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False}
        }
        # populates the dictionary of "unseen" cards. before play begins, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self._unseen_cards.append(str(card))

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
        self._hand.sort(key=lambda x: x.sort_key)
        return [str(c) for c in self._hand]

    # AGENT API FUNCTION new_hand(self, names)
    #
    # Takes a list of names of all agents in the game in clockwise order
    # and returns nothing. This method is also responsible for clearing any data
    # necessary for your agent to start a new round.
    #
    def new_hand(self, names):
        self._players = names
        self.playerID = names.index(self.get_name())
        self._tricks_taken = 0
        # flag to indicate when a particular player is known to be out of a particular suit
        # useful anytime as it hints at the distribution of cards, but will be particularly useful
        # when trumps are introduced...
        self._player_out_of_suit = {
            0: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            1: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            2: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False},
            3: {OCSCard.SPADES: False, OCSCard.HEARTS: False, OCSCard.CLUBS: False, OCSCard.DIAMONDS: False}
        }
        # list of all cards in your hand
        self._hand = []
        # tracks all cards the agent has not "seen" either in it's own hand or played in a trick
        self._unseen_cards = []
        self.state = None
        # populates the dictionary of "unseen" cards. before play begins, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self._unseen_cards.append(str(card))
    
    # AGENT API FUNCTION add_cards_to_hand(self, cards)
    #
    # A method that takes a single argument, a list of two character strings representing cards to be
    # added to the agent's hand. This is used for dealing and psssing and so should be able to take a
    # list of length of any length. This method should return nothing
    #
    def add_cards_to_hand(self, cards):
        for c in cards:
            assert(len(c) == 2)
            rank = OCSCard.ranks.index(c[0])
            suit = OCSCard.suits.index(c[1])
            card = OCSCard(rank, suit)
            self._hand.append(card)
            self.mark_as_seen(c)
        
    # UTILITY FUNCTION markup_status_of_cards_in_trick(self, trick)
    #
    # Analyzes the cards in the trick parameter, marks them as having been played already
    # and makes note of any players not able to follow suit.
    #
    def markup_status_of_cards_in_trick(self, trick):
        # make sure all cards that were played in the trick are flagged as seen
        suit_led = None
        for i, c in enumerate(trick):
            rank = OCSCard.ranks.index(c[0])
            suit = OCSCard.suits.index(c[1])
            card = OCSCard(rank, suit)
            self.mark_as_seen(c)
            # if suit_led is None, this is the first card in the trick so save it
            if suit_led is None:
                suit_led = card.suit
            # this the 2nd, 3rd, or 4th card in the trick. if the suit_led doesn't
            # match the first card, mark the 
            if card.suit != suit_led:
                self._player_out_of_suit[i][card.suit] = True
                
    # AGENT API FUNCTION play_card(self, lead, trick)
    #
    # Redefine this procedure for inherited classes that implement different techniques
    # for choosing which card to play
    #
    def play_card(self, lead, trick):
        pass

    # AGENT API FUNCTION: collect_trick(self, lead, winner, trick)
    #
    # Takes 3 arguments. A string of the name of the player who led the trick, a string of the name of
    # the player who won the trick, and a list of the twi character strings representing the card in the
    # trick in the order they were played, starting with the lead.
    #
    def collect_trick(self, lead, winner, trick):
        # if you're the winner of the trick, increment the number of tricks taken
        if self.get_name() == winner:
            self._tricks_taken += 1
        self.markup_status_of_cards_in_trick(trick)
        
    # AGENT API FUNCTION: score(self)
    #
    # Takes no arguments and returns an integer of the number of point your agent scored on this hand.
    #
    def score(self):
        return self._tricks_taken


# Class representing the Player
class Player(BasePlayer):
    def __init__(self):
        BasePlayer.__init__(self, "Organic Chem Survivors")
        
    # This function is called every time the agent is asked to play a card. It
    # splits the cards in the agent's hand and the remeaining outstanding (unseen)
    # cards into rank-ordered groups by suit. These variables make it easier to
    # make decisions in the code.
    #
    def mark_as_seen(self, card):
        if card in self._unseen_cards:
            self._unseen_cards.remove(card)
        
    # Get a list of suits in your hand ordered by the number of cards you have in each suit.
    def order_suits_by_count(self, card_count):
        return [suit for _, suit in sorted([(v, i) for i, v in enumerate(card_count) if v > 0])]
    
    # Looks for potentially exploitable card patterns to inform strategy. For example, a high suit count
    # with the more winners tha potential full rounds would get a human to "try to run the suit" as a strategy
    # for that suit. Same when leading with any suit you alone hold (in the absence of trumps).
    # Returns a non-winner card that will hopefully lead to the promotion of another card in the suit if one
    # exits.
    def find_most_promising_lead(self):
        all_unplayed_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        order_of_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        suits_by_count = self.order_suits_by_count(self._state._card_count)

        for suit in suits_by_count:
            # only consider suits where you actually have a card to play...
            if self._state._cards[suit] != []:
                all_unplayed_cards[suit] = self._state._cards[suit] + self._state._outstanding_cards[suit]
                all_unplayed_cards[suit].sort(reverse=True)
                st = set(self._state._cards[suit])
                for idx, val in enumerate(all_unplayed_cards[suit]):
                    if val in st:
                        order_of_cards[suit].append((idx, val))

        # Now cards are arranged in order of importance. We know winners (importance 0) "should be" played
        # by the lead routine, so we to look for any suit with cards of importance 1 in cards we have more
        # than 1 card and lead the lower card to try to promote that first card
        #
        # Heuristic #1: Fish for a suit where you might be able to promote the rank 1 ordered by suit length
        for suit in suits_by_count: # b is a list of suits with at least 1 card
            for i in range(len(order_of_cards[suit])):
                order, rank = order_of_cards[suit][i]
                # quick shortcut...if somehow this was the best card in the suit, play it!
                if order == 0:
                    return OCSCard(rank, suit)
                # otherwise, if suits have more than 1 card look for a suit with the second
                # highest card. If you find one, play the next highest card in the suit you
                # have trying to flush out that higher card
                if len(order_of_cards[suit]) > 1:
                    if order == 1:
                        if i+1 < len(order_of_cards[suit]):
                            order, rank = order_of_cards[suit][i+1]
                            return OCSCard(rank, suit)
                # the suit must have 1 card. If it's order is low, discard it
                else:
                    low_order = math.floor(len(all_unplayed_cards[suit]) / 2)
                    if order > low_order:
                        return OCSCard(rank, suit)
        return None
                
    def find_most_promising_follow(self, suit):
        # Shorcut: Return None if this function was called on an empty suit
        if self._state._card_count[suit] == 0:
            return None
        all_unplayed_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        order_of_cards = {OCSCard.SPADES: [], OCSCard.HEARTS: [], OCSCard.CLUBS: [], OCSCard.DIAMONDS: []}
        b = self.order_suits_by_count(self._state._card_count)
        # only consider suits where you actually have a card to play...
        if self._state._cards[suit] != []:
            all_unplayed_cards[suit] = self._state._cards[suit] + self._state._outstanding_cards[suit]
            all_unplayed_cards[suit].sort(reverse=True)
            st = set(self._state._cards[suit])
            for idx, val in enumerate(all_unplayed_cards[suit]):
                if val in st:
                    order_of_cards[suit].append((idx, val))

        # Now cards are arranged in order of importance. We know winners (importance 0) should be played
        # by the lead routine, so we to look for any suit with cards of importance 1 in cards we have more
        # than 1 card and lead the lower card to try to promote that first card
        #
        # Heuristic #1: Fish for a suit where you might be able to promote the rank 1 ordered by suit length
        for i in range(len(order_of_cards[suit])):
            order, rank = order_of_cards[suit][i]
            # quick shortcut...if somehow this was the best card in the suit, play it!
            if order == 0:
                return OCSCard(rank, suit)
            # otherwise, if suits have more than 1 card look for a suit with the second
            # highest card. If you find one, play the next highest card in the suit you
            # have trying to flush out that higher card
            if len(order_of_cards[suit]) > 1:
                if order == 1:
                    if i+1 < len(order_of_cards[suit]):
                        order, rank = order_of_cards[suit][i+1]
                        return OCSCard(rank, suit)
            # the suit must have 1 card. If it's order is low, discard it
            else:
                low_order = math.floor(len(all_unplayed_cards[suit]) / 2)
                if order > low_order:
                    return OCSCard(rank, suit)
        return None


    # AGENT API FUNCTION play_card(self, lead, trick)
    #
    # This will likely be the bulk of your code. This method takes two arguments, the name of the
    # player who is leading the trick, and a list of two character strings of the cards that have
    # been played so far this trick. This method should return a single two character string
    # representing the card your agent has chosen to play. From this method your agent should also
    # track which cards are left in its hand.

    # The majority of "strategic" play takes place relative early in the hand when cards are plentiful.
    # Later in the hand, your choices become increasingly limited, particularly when you're not leading.

    # This first attempt at an AI agent will use a simplification based in part on the no-trump assumption.
    # It will assume all cards of a particular not in a suit are uniformly distributed across other hands.
    # This doesn't seem like a "terrible" assumption to make as discards of worthless cards in other suits
    # "could" be useless. Where it's vulnerable are hands with a highly skewed distribution of cards - but
    # human players can also be dominated by highly unlikely card distributions.

    # With this assumption, the "min" agent will always try to take the trick away from you with the highest
    # card in it's hand and discard 2 low cards or discard 3 low cards if it will certainly lose.

    # Your opportunities when not in the lead are to take the trick if you can or discard (sluff). You will
    # will always try to choose what you view as the most useless card in your hand to discard.

    # Where you get to attempt to play a real strategy is going to be limited to leading a trick. Here you
    # will take all the tricks you can and then try to use a min-max tree to choose which losing card to
    # lead. You should not try any finesse from the lead position because you're assumption is that your
    # opponent will always take the trick with a higher card.

    # In version 1 of this code, there are no trumps. What you play is determined by your
    # playing order in the trick.
    #
    # If you're the lead in on the trick, you get to choose what to play. The initial strategy
    # is to attempt to play all your winning cards first (either the highest card in the suit or
    # any suits you alone hold). Otherwise play the lowest card in a suit.
    #
    # If you're not the lead on the trick, you must follow suit if you can. You can take the trick
    # if you have the highest card in the suit (obviously), or you can sluff off the trick (play low),
    # or, if you're the last player in the trick, you can take it with the lowest possible card. If
    # you have more than 2 cards, you could choose to play your 2nd highest card but would only want
    # to do that if it is higher than cards already played.
    #
    # If you're not in the lead and cannot follow suit, in spades or bridge you could play a trump if
    # there is a trump suit. Otherwise, all you can do is discard a card of another suit. Any strategy
    # involved here is involved in choosing which suit and rank to discard. If you're strong in another
    # suit, keep those cards.

    def play_card(self, lead, trick):

        # does the trick contain any cards in the current suit? if so, get the highest card
        def highest_card_played_in_suit(suit, trick):
            highest_rank = -1
            for i in trick:
                card = OCSCard.create(i)
                if card.suit == suit:
                    if card.rank > highest_rank:
                        highest_rank = card.rank
            return highest_rank

        def drop_card(rank, suit):
            # since you're playing this card, remove it from your hand
            card = OCSCard(rank, suit)
            self._hand.remove(card)
            return OCSCard.ranks[rank] + OCSCard.suits[suit]

        # Pick a card to lead. Allows you to pick both the suit to lead and the card.
        def pick_a_card_to_lead_with():
            # Check for winners and play them
            for suit, rank in self._state._cards.items():
                # if you have a potential winner, play it...
                if self._state._card_count[suit] > 0:
                    # if all other players are out of the suit or it's the highest card still in the suit, play it
                    if self._state._outstanding_card_count[suit] == 0 or self._state._cards[suit][-1] > self._state._outstanding_cards[suit][-1]:
                        return OCSCard(self._state._cards[suit][-1], suit)
            card = self.find_most_promising_lead()
            if card is not None:
                return card
            # Don't believe you have any winners right now, so pick another card.
            # Simple trategy at this point: Try to pick a the lowest card in a suit where you have at least
            # 2 cards with the hope you promote your other card to a winner...
            if self._state._card_count[OCSCard.HEARTS] > 1 or self._state._card_count[OCSCard.CLUBS] > 1 or self._state._card_count[OCSCard.DIAMONDS] > 1 or self._state._card_count[OCSCard.SPADES] > 1:
                # candidate suits are suits with more than 1 card
                candidates = [(self._state._cards[i][0], i) for i, j in enumerate(self._state._card_count) if j > 1]
                lowest_rank, lowest_suit = min(candidates, key=operator.itemgetter(1))
                return OCSCard(lowest_rank, lowest_suit)
            # Late in the hand, you will have 1 or fewer cards in each trick
            else:
                # candidate suits are theoretically reduced to cards with just 1 card with just 1 card
                # so get a list of the suits that still have 1 cards left in them
                # then find and lead the highest
                # TODO: Switch to the logic used in play_a_card_to_discard to deliberately play
                #       winners, if you can...
                candidates = [(self._state._cards[i][0], i) for i, j in enumerate(self._state._card_count) if j > 0]
                if len(candidates) > 0:
                    highest_rank, highest_suit = max(candidates, key=operator.itemgetter(0))
                    return OCSCard(highest_rank, highest_suit)

        def pick_a_card_to_follow_suit(suit_led):
            # Shortcut 1: If you only have 1 card in the suit led, you must play it
            if len(self._state._cards[suit_led]) == 1:
                return OCSCard(self._state._cards[suit_led][0], suit_led)
            
            highest_card_in_trick = highest_card_played_in_suit(suit_led, trick)
            max_card_in_suit = self._state._cards[suit_led][-1]
            min_card_in_suit = self._state._cards[suit_led][0]
            # Shortcut 2: If your best card will lose the trick, dump the lowest card in the suit 
            # in the hope that it promotes another card to a winner eventually...
            if max_card_in_suit < highest_card_in_trick:
                return OCSCard(min_card_in_suit, suit_led)
            else:
                # In this branch, you have a card that is higher than one previously played in the trick.
                # Shorcut 3: If you're the last player in the trick, take it with the lowest possible card...
                if len(trick) == 3:
                    return OCSCard(min(list(filter(lambda x: x > highest_card_in_trick, self._state._cards[suit_led]))), suit_led)
                # If you survived to here, you must be the 2nd or 3rd player in the trick and have a potential winner
                # Shorcut 4: If your high card is the only one of the suit remaining or is the highest card in the suit,
                # play it to win the trick and take control of play.
                if len(self._state._outstanding_cards[suit_led]) == 0 or max_card_in_suit > self._state._outstanding_cards[suit_led][-1]:
                    return OCSCard(max_card_in_suit, suit_led)
                # otherwise, decide whether you want to risk or just discard your lowest card
                else:
                    card = self.find_most_promising_follow(suit_led)
                    # a simple finesse is possible here
                    if card is not None:
                       if card.rank > highest_card_in_trick:
                            return(card)
                    return OCSCard(min_card_in_suit, suit_led)

        # Pick a non-led card to discard. This procedure chooses a card to play when you
        # can't follow suit. It assumes you have already tried to follow suit but cannot
        # and doesn't check to ensure it...
        def pick_a_non_led_card_to_discard():
            # If you have a large number of cards in a particular suit (say, greater than
            # the potential number of full roundss of that suit + 1), then first look to
            # see if you have any suits with just 2 cards and 1 is a guaranteed winner
            # and the other is not at this point. Rationale: Save the higher card to take a
            # trick and hope the suit with the most cards in your hand can
            # become dominant.
            have_lots_of_these_suits = []
            for i in range(OCSCard.NR_SUITS):
                if self._state._card_count[i] > self._state._potential_full_rounds[i] + 1:
                    have_lots_of_these_suits.append(i)
            long_suits = [OCSCard.suits[s] for s in have_lots_of_these_suits]
            for i in range(OCSCard.NR_SUITS):
                if len(have_lots_of_these_suits) == 0 and i not in have_lots_of_these_suits:
                    if self._state._outstanding_card_count[i] >= 2 and self._state._card_count[i] == 2:
                        if self._state._cards[i][-1] > self._state._outstanding_cards[i][-1] and self._state._cards[i][-2] < self._state._outstanding_cards[i][-1]:
                            return OCSCard(self._state._cards[i][0], i)
            # otherwise, find the suit with the lowest loser card
            loser_suit = None
            loser_rank = 99
            for i in range(OCSCard.NR_SUITS):
                if len(self._state._non_winners[i]) > 0:
                    if self._state._non_winners[i][0] < loser_rank:
                        loser_rank = self._state._non_winners[i][0]
                        loser_suit = i
            if loser_suit is not None:
                return OCSCard(loser_rank, loser_suit)
            # all cards are winners, so discard the lowest_winner
            if loser_suit is None:
                lowest_winner_suit = None
                lowest_winner_rank = 99
                for i in range(OCSCard.NR_SUITS):
                    if len(self._state._potential_winners[i]) > 0:
                        if self._state._potential_winners[i][0] < lowest_winner_rank:
                            lowest_winner_rank = self._state._potential_winners[i][0]
                            lowest_winner_suit = i
            if lowest_winner_suit is not None:
                  return OCSCard(lowest_winner_rank, lowest_winner_suit)

        # BEGIN BODY OF play_card   #########################################################
        #

        self._hand.sort(key=lambda x: x.sort_key)
        self._state = State(self._hand, self._unseen_cards)
        # If no cards in the trick so far, it's the first time so you get to pick any card
        if len(trick) == 0:
            card = pick_a_card_to_lead_with()
            suit_led = card.suit
            return drop_card(card.rank, card.suit)
        else:
            # else, if you can follow suit, you must follow suit
            suit_led = OCSCard.create(trick[0]).suit
            if len(self._state._cards[suit_led]) > 0:
                card = pick_a_card_to_follow_suit(suit_led)
                return drop_card(card.rank, card.suit)
            # finally, if you don't have a card in the suit, you must still pick a card
            # (hopefully a losing card) from one of the other suits to discard
            else:
                card = pick_a_non_led_card_to_discard()
                return drop_card(card.rank, card.suit)
        #
        # END BODY OF play_card     #########################################################
