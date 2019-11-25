import math
import random
import operator
import numpy

# Simple class representing a card
class Card:
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
        rank = Card.ranks.index(string[0])
        suit = Card.suits.index(string[1])
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
##        if self.suit == Card.SPADES:
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
        # a copy of the hand used to maintain its initial state for printing out later
        self._hand_copy = []
        self.unseen_cards = []
        # list of all cards that the agent hasn't seen (either in its own hand or played in a trick)
        # the cards in your hand broken down by suit (and ordered by rank)
        self.__cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__card_count = [0, 0, 0, 0]
        # the unseen cards broken down by suit (and ordered by rank)
        self.__outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__outstanding_card_count = [0, 0, 0, 0]
        # maximum number of full rounds that could be played by suit if the outstanding cards are
        # uniformly distributed
        self.__potential_full_rounds = [0, 0, 0, 0]
        # flag to indicate when a particular player is known to be out of a particular suit
        # useful anytime as it hints at the distribution of cards, but will be particularly useful
        # when trumps are introduced...
        self.__player_out_of_suit = {
            0: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            1: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            2: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            3: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False}
        }
        # For future use:
        # self.__bid = 0
        self.__tricks_won = 0
        # populates the dictionary of "unseen" cards. before play begins, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self.unseen_cards.append(str(card))

    # This function is called every time the agent is asked to play a card. It
    # splits the cards in the agent's hand and the remeaining outstanding (unseen)
    # cards into rank-ordered groups by suit. These variables make it easier to
    # make decisions in the code.
    #
    def arrange_cards(self):
        self.__cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__card_count = [0, 0, 0, 0]
        self.__outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__outstanding_card_count = [0, 0, 0, 0]
        # called "potential" winners instead of guaranteed winners in anticipation of trumps being
        # introduced into the game...
        self.__potential_winners = [ [], [], [], [] ]
        self.__non_winners = [ [], [], [], [] ]
        for card in self._hand:
            self.__cards[card.suit].append(card.rank)
        for card in self.unseen_cards:
            rank = Card.ranks.index(card[0])
            suit = Card.suits.index(card[1])
            self.__outstanding_cards[suit].append(rank)
        for suit in range(Card.NR_SUITS):
            self.__cards[suit].sort()
            self.__card_count[suit] = len(self.__cards[suit])
            self.__outstanding_cards[suit].sort()
            self.__outstanding_card_count[suit] = len(self.__outstanding_cards[suit])
            if self.__card_count[suit] > 0:
                for j in range(self.__card_count[suit]):
                    if self.__outstanding_card_count[suit] == 0:
                        # there are no outstanding cards in this suit, so in the absence of trump these are winners
                        self.__potential_winners[suit].append(self.__cards[suit][j])
                    elif self.__cards[suit][j] > self.__outstanding_cards[suit][-1]:
                        # cards greater than the highest outstanding suit
                        self.__potential_winners[suit].append(self.__cards[suit][j])
                    else:
                        # these cards could be beaten by another player at this point, so they shouldn't be used
                        # as leads if you expect to win...viewing all of the opponents as cutthroat players
                        self.__non_winners[suit].append(self.__cards[suit][j])
            # print("winners:", potential_winners)
            # print("non-winners:", non_winners)
        # The maximum number of full rounds possible assuming a uniform distribution of outstanding cards
        # is just the number of outstanding cards divided by 3 and rounded down. There is, of course, no
        # guarantee the cards are uniformly distributed. In fact, it's unlikely. This is just used as a
        # simple heuristic to decide whether or not a card has potential as a winner
        self.__potential_full_rounds = [math.floor(x/3) for x in self.__outstanding_card_count]
        #print("my card count", self.__card_count, "outstanding card count:", self.__outstanding_card_count)

    def mark_as_seen(self, card):
        if card in self.unseen_cards:
            self.unseen_cards.remove(card)
        assert card not in self.unseen_cards, print(card, 'in', self.unseen_cards)
        
    # Looks for potentially exploitable card patterns to inform strategy. For example, a high suit count
    # with the more winners tha potential full rounds would get a human to "try to run the suit" as a strategy
    # for that suit. Same when leading with any suit you alone hold (in the absence of trumps).
    # Returns a non-winner card that will hopefully lead to the promotion of another card in the suit if one
    # exits.
    def find_most_promising_lead(self):
        all_unplayed_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        order_of_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        a = [(v, i) for i, v in enumerate(self.__card_count) if v > 0]
        a.sort()
        b = []
        for v in a:
            _, value = v
            b.append(value)
        #print('a', a, 'b', b)
        for suit in b:
            # only consider suits where you actually have a card to play...
            if self.__cards[suit] != []:
                all_unplayed_cards[suit] = self.__cards[suit] + self.__outstanding_cards[suit]
                all_unplayed_cards[suit].sort(reverse=True)
                st = set(self.__cards[suit])
                for idx, val in enumerate(all_unplayed_cards[suit]):
                    if val in st:
                        order_of_cards[suit].append((idx, val))
        #print(order_of_cards)
        # Now cards are arranged in order of importance. We know winners (importance 0) should be played
        # by the lead routine, so we to look for any suit with cards of importance 1 in cards we have more
        # than 1 card and lead the lower card to try to promote that first card
        #
        # Heuristic #1: Fish for a suit where you might be able to promote the rank 1 ordered by suit length
        for suit in b: # b is a list of suits with at least 1 card
            for i in range(len(order_of_cards[suit])):
                order, rank = order_of_cards[suit][i]
                # print(order_of_cards[suit][i])
                # quick shortcut...if somehow this was the best card in the suit, play it!
                if order == 0:
                    return Card(rank, suit)
                # otherwise, if suits have more than 1 card look for a suit with the second
                # highest card. If you find one, play the next highest card in the suit you
                # have trying to flush out that higher card
                if len(order_of_cards[suit]) > 1:
                    if order == 1:
                        if i+1 < len(order_of_cards[suit]):
                            order, rank = order_of_cards[suit][i+1]
                            return Card(rank, suit)
                # the suit must have 1 card. If it's order is low, discard it
                else:
                    low_order = math.floor(len(all_unplayed_cards[suit]) / 2)
                    if order > low_order:
                        return Card(rank, suit)
        return None
                
    def find_most_promising_follow(self, suit):
        #print("find most promising follow called")
        all_unplayed_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        order_of_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        a = [(v, i) for i, v in enumerate(self.__card_count) if v > 0 if i == suit]
        a.sort()
        b = []
        for v in a:
            _, value = v
            b.append(value)
        #print('b was:', b)
        # only consider suits where you actually have a card to play...
        if self.__cards[suit] != []:
            all_unplayed_cards[suit] = self.__cards[suit] + self.__outstanding_cards[suit]
            all_unplayed_cards[suit].sort(reverse=True)
            st = set(self.__cards[suit])
            for idx, val in enumerate(all_unplayed_cards[suit]):
                if val in st:
                    order_of_cards[suit].append((idx, val))
        # print(order_of_cards)
        if len(order_of_cards[suit]) == 0:
            #print("apparently order of cards[suit] had length 0")
            return None
        # Now cards are arranged in order of importance. We know winners (importance 0) should be played
        # by the lead routine, so we to look for any suit with cards of importance 1 in cards we have more
        # than 1 card and lead the lower card to try to promote that first card
        #
        # Heuristic #1: Fish for a suit where you might be able to promote the rank 1 ordered by suit length
        for i in range(len(order_of_cards[suit])):
            order, rank = order_of_cards[suit][i]
            # print(order_of_cards[suit][i])
            # quick shortcut...if somehow this was the best card in the suit, play it!
            if order == 0:
                return Card(rank, suit)
            # otherwise, if suits have more than 1 card look for a suit with the second
            # highest card. If you find one, play the next highest card in the suit you
            # have trying to flush out that higher card
            if len(order_of_cards[suit]) > 1:
                if order == 1:
                    if i+1 < len(order_of_cards[suit]):
                        order, rank = order_of_cards[suit][i+1]
                        return Card(rank, suit)
            # the suit must have 1 card. If it's order is low, discard it
            else:
                low_order = math.floor(len(all_unplayed_cards[suit]) / 2)
                if order > low_order:
                    return Card(rank, suit)
        return None


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
        self._hand_copy = []
        self.unseen_cards = []
        self.__cards.clear()
        self.__cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__card_count = [0, 0, 0, 0]
        self.__outstanding_cards.clear()
        self.__outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__outstanding_card_count = [0, 0, 0, 0]
        self.__potential_full_rounds = [0, 0, 0, 0]
        self.__player_out_of_suit.clear()
        self.__player_out_of_suit = {
            0: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            1: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            2: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            3: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False}
        }
        self.__bid = 0
        self.__tricks_won = 0
        # represents knowledge about what cards this player has seen at any point.
        # before receiving your hand, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self.unseen_cards.append(str(card))
    
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
            rank = Card.ranks.index(c[0])
            suit = Card.suits.index(c[1])
            card = Card(rank, suit)
            self.mark_as_seen(c)
            # if suit_led is None, this is the first card in the trick so save it
            if suit_led is None:
                suit_led = card.suit
            # this the 2nd, 3rd, or 4th card in the trick. if the suit_led doesn't
            # match the first card, mark the 
            if card.suit != suit_led:
                self.__player_out_of_suit[i][card.suit] = True
                
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
                card = Card.create(i)
                if card.suit == suit:
                    if card.rank > highest_rank:
                        highest_rank = card.rank
            return highest_rank

        def drop_card(rank, suit):
            # since you're playing this card, remove it from your hand
            card = Card(rank, suit)
            print("{0} played {1} from hand {2}".format(self.name, card, self._hand))
            self._hand.remove(card)
            #self.mark_as_seen(str(card))
            return Card.ranks[rank] + Card.suits[suit]

        # Pick a card to lead. Allows you to pick both the suit to lead and the card.
        def pick_a_card_to_lead_with():
            # Check for winners and play them
            for suit, rank in self.__cards.items():
                # if you have a potential winner, play it...
                if self.__card_count[suit] > 0:
                    # if all other players are out of the suit or it's the highest card still in the suit, play it
                    if self.__outstanding_card_count[suit] == 0 or self.__cards[suit][-1] > self.__outstanding_cards[suit][-1]:
                        return Card(self.__cards[suit][-1], suit)
            card = self.find_most_promising_lead()
            if card is not None:
                return card
            # Don't believe you have any winners right now, so pick another card.
            # Simple trategy at this point: Try to pick a the lowest card in a suit where you have at least
            # 2 cards with the hope you promote your other card to a winner...
            if self.__card_count[Card.HEARTS] > 1 or self.__card_count[Card.CLUBS] > 1 or self.__card_count[Card.DIAMONDS] > 1 or self.__card_count[Card.SPADES] > 1:
                # candidate suits are suits with more than 1 card
                candidates = [(self.__cards[i][0], i) for i, j in enumerate(self.__card_count) if j > 1]
                lowest_rank, lowest_suit = min(candidates, key=operator.itemgetter(1))
                return Card(lowest_rank, lowest_suit)
            # Late in the hand, you will have 1 or fewer cards in each trick
            else:
                # candidate suits are theoretically reduced to cards with just 1 card with just 1 card
                # so get a list of the suits that still have 1 cards left in them
                # then find and lead the highest
                # TODO: Switch to the logic used in play_a_card_to_discard to deliberately play
                #       winners, if you can...
                candidates = [(self.__cards[i][0], i) for i, j in enumerate(self.__card_count) if j > 0]
                # print("candidates check 2:", candidates)
                if len(candidates) > 0:
                    highest_rank, highest_suit = max(candidates, key=operator.itemgetter(0))
                    # print("returning 2:", Card(highest_rank, highest_suit))
                    return Card(highest_rank, highest_suit)

        def pick_a_card_to_follow_suit(suit_led):
            # Quick shortcut. If you only have 1 card in the suit led, you must play it
            if len(self.__cards[suit_led]) == 1:
                return Card(self.__cards[suit_led][0], suit_led)
            # Otherwise, find out the highest card outstanding and the max and min cards in
            # the suit in the agent's hand...
            highest_card_in_trick = highest_card_played_in_suit(suit_led, trick)
            max_card_in_suit = self.__cards[suit_led][-1]
            min_card_in_suit = self.__cards[suit_led][0]
            # If you can't win, dump the lowest card in the suit in the hope that it promotes another
            # card to a winner eventually. Without team play, there is less motivation to try to play
            # higher non-winners hoping your partner is holding
            if max_card_in_suit < highest_card_in_trick:
                return Card(min_card_in_suit, suit_led)
            else:
                # you "could" play a card above the current trick winner, but should you?
                # well, if you're the last player in the trick and since you're not not concerned without
                # penalties for going over your bid, take it with the lowest possible card
                if len(trick) == 3:
                    return Card(min(list(filter(lambda x: x > highest_card_in_trick, self.__cards[suit_led]))), suit_led)
                # otherwise, we should be in tricks 2 or 3 here
                # if you have the highest card remaining, play it
                # DEBUGGING CODE for evaluating whether or not a simple finesse might be attempted
                # When using min-max (or something else), we can get rid of heuristics...
                if len(self.__outstanding_cards[suit_led]) > 0:
                    print('outstanding cards in suit', [c + 2 for c in self.__outstanding_cards[suit_led]],
                          'max card you hold', max_card_in_suit+2,
                          'highest card played', highest_card_in_trick+2,
                          'highest card still hidden', self.__outstanding_cards[suit_led][-1]+2)
                if len(self.__outstanding_cards[suit_led]) == 0 or max_card_in_suit > self.__outstanding_cards[suit_led][-1]:
                    return Card(max_card_in_suit, suit_led)
                # otherwise, hold it in reserve and drop the lowest card if you can
                else:
                    card = self.find_most_promising_follow(suit_led)
                    if card is not None:
                        print('flagged card:', card, 'highest_card', highest_card_in_trick)
                        if card.rank > highest_card_in_trick:
                            return(card)
                    return Card(min_card_in_suit, suit_led)

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
            for i in range(Card.NR_SUITS):
                if self.__card_count[i] > self.__potential_full_rounds[i] + 1:
                    have_lots_of_these_suits.append(i)
            long_suits = [Card.suits[s] for s in have_lots_of_these_suits]
            for i in range(Card.NR_SUITS):
                if len(have_lots_of_these_suits) == 0 and i not in have_lots_of_these_suits:
                    if self.__outstanding_card_count[i] >= 2 and self.__card_count[i] == 2:
                        if self.__cards[i][-1] > self.__outstanding_cards[i][-1] and self.__cards[i][-2] < self.__outstanding_cards[i][-1]:
                            print("card drop to promote other card:", Card(self.__cards[i][0], i))
                            return Card(self.__cards[i][0], i)
            # otherwise, find the suit with the lowest loser card
            loser_suit = None
            loser_rank = 99
            for i in range(Card.NR_SUITS):
                if len(self.__non_winners[i]) > 0:
                    if self.__non_winners[i][0] < loser_rank:
                        loser_rank = self.__non_winners[i][0]
                        loser_suit = i
            if loser_suit is not None:
                return Card(loser_rank, loser_suit)
            # all cards are winners, so discard the lowest_winner
            if loser_suit is None:
                lowest_winner_suit = None
                lowest_winner_rank = 99
                for i in range(Card.NR_SUITS):
                    if len(self.__potential_winners[i]) > 0:
                        if self.__potential_winners[i][0] < lowest_winner_rank:
                            lowest_winner_rank = self.__potential_winners[i][0]
                            lowest_winner_suit = i
            if lowest_winner_suit is not None:
                  return Card(lowest_winner_rank, lowest_winner_suit)

        # BEGIN BODY OF play_card   #########################################################
        #

        self._hand.sort(key=lambda x: x.sort_key)
        self.arrange_cards()
        
        # If no cards in the trick so far, it's the first time so you get to pick any card
        if len(trick) == 0:
            card = pick_a_card_to_lead_with()
            suit_led = card.suit
            return drop_card(card.rank, card.suit)
        else:
            # else, if you can follow suit, you must follow suit
            suit_led = Card.create(trick[0]).suit
            if len(self.__cards[suit_led]) > 0:
                card = pick_a_card_to_follow_suit(suit_led)
                return drop_card(card.rank, card.suit)
            # finally, if you don't have a card in the suit, you must still pick a card
            # (hopefully a losing card) from one of the other suits to discard
            else:
                card = pick_a_non_led_card_to_discard()
                return drop_card(card.rank, card.suit)
        #
        # END BODY OF play_card     #########################################################

    # AGENT API FUNCTION: collect_trick(self, lead, winner, trick)
    #
    # Takes 3 arguments. A string of the name of the player who led the trick, a string of the name of
    # the player who won the trick, and a list of the twi character strings representing the card in the
    # trick in the order they were played, starting with the lead.
    #
    def collect_trick(self, lead, winner, trick):
        # if you're the winner of the trick, increment the number of tricks taken
        if self.get_name() == winner:
            self.__trick_taken += 1
        self.markup_status_of_cards_in_trick(trick)
        
    # AGENT API FUNCTION: score(self)
    #
    # Takes no arguments and returns an integer of the number of point your agent scored on this hand.
    #
    def score(self):
        return self.__trick_taken


class OCS_Team1(Player):
    def __init__(self):
        Player.__init__(self, "Matt")

class OCS_Team2(Player):
    def __init__(self):
        Player.__init__(self, "Mark")

class OCS_Team3(Player):
    def __init__(self):
        Player.__init__(self, "Luke")

class OCS_Team4(Player):
    def __init__(self):
        Player.__init__(self, "John")

