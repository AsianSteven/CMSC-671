from card import Card
from deck import Deck
import math
import operator

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
        # list of all cards that the agent hasn't seen (either in its own hand or played in a trick)
        self.__unseen_cards = {}
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
            self.__unseen_cards[card] = True

    # This function is called every time the agent is asked to play a card. It
    # splits the cards in the agent's hand and the remeaining outstanding (unseen)
    # cards into rank-ordered groups by suit. These variables make it easier to
    # make decisions in the code.
    #
    def __arrange_cards__(self):
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
        for card in self.__unseen_cards:
            if self.__unseen_cards[card]:
                self.__outstanding_cards[card.suit].append(card.rank)
        for suit in range(4):
            self.__cards[suit].sort()
            self.__card_count[suit] = len(self.__cards[suit])
            self.__outstanding_cards[suit].sort()
            self.__outstanding_card_count[suit] = len(self.__outstanding_cards[suit])
            if self.__card_count[suit] > 0:
                for j in range(self.__card_count[suit]):
                    if self.__outstanding_card_count[suit] > 0 and self.__cards[suit][j] > self.__outstanding_cards[suit][-1]:
                        # cards greater than the highest outstanding suit
                        print('debug: adding max card in suit', Card(self.__cards[suit][j], suit))
                        self.__potential_winners[suit].append(self.__cards[suit][j])
                    elif self.__outstanding_card_count[suit] == 0:
                        # there are no outstanding cards in this suit, so in the absence of trump these are winners
                        print('debug: no cards (other than mine) exist in the suit:', Card.suits[suit])
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
        self.__unseen_cards = {}
        self.__cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__card_count = [0, 0, 0, 0]
        self.__outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.__outstanding_card_count = [0, 0, 0, 0]
        self.__potential_full_rounds = [0, 0, 0, 0]
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
            self.__unseen_cards[card] = True
    
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
            self.__unseen_cards[card] = False
        
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
            self.__unseen_cards[card] = False
            # if suit_led is None, this is the first card in the trick so save it
            if suit_led is None:
                suit_led = card.suit
            # this the 2nd, 3rd, or 4th card in the trick. if the suit_led doesn't
            # match the first card, mark the 
            if card.suit != suit_led:
                self.__player_out_of_suit[i][card.suit] = True
                
    # AGENT API FUNCTION play_card(self, lead, trick)
    #
    # This will likely be the bulk of your code. This method takes two
    # arguments, the name of the player who is leading the trick, and a
    # list of two character strings of the cards that have been played
    # so far this trick. This method should return a single two character
    # string representing the card your agent has chosen to play. From
    # this method your agent should also track which cards are left in
    # its hand.

    # ** This is an important procedure for future modification **
    # It starts by simply playing the highest card it has in the suit it must follow
    #    NOTE: This does not use any real AI techniques yet, just some basic
    #          rules of thumb such as:
    #          1. If you have the highest unplayed card in the suit played, play it to take the round.
    #          2. If you cannot win the trick, play the lowest card in the suit played.
    #          3. If you cannot follow suit, play the lowest card in another suit.


    # POTENTIAL PLAYS
    # 1. Try to win a trick by playing the highest card in the suit
    # 2. Discard a card by playing the lowest card in the quit OR another non-spade
    # 3. Slough off a card by playing the highest "non-winner" you have (to reduce the
    #    chance of unwanted tricks later in the round)

    def play_card(self, lead, trick):

        # does the trick contain any cards in the current suit?
        # if so, get the highest card
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
            print("{0} played {1} from hand {2}".format(self.name, Card(rank, suit), self._hand))
            self._hand.remove(Card(rank, suit))
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
            # Don't believe you have any winners right now, so pick another card.
            # Simple trategy at this point: Try to pick a the lowest card in a suit where you have at least
            # 2 cards with the hope you promote your other card to a winner...
            if self.__card_count[Card.HEARTS] > 1 or self.__card_count[Card.CLUBS] > 1 or self.__card_count[Card.DIAMONDS] > 1 or self.__card_count[Card.SPADES] > 1:
                # candidate suits are suits with more than 1 card
                candidates = [(self.__cards[i][0], i) for i, j in enumerate(self.__card_count) if j > 1]
                # print("candidates check 1:", candidates)
                lowest_rank, lowest_suit = min(candidates, key=operator.itemgetter(1))
                # print("returning 1:", Card(lowest_rank, lowest_suit))
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
            #
            # If it's past the first turn (turns 2-4), you must follow suit if you can.
            # If you're in turns 2-3, you can try to take the trick if you have the highest card of
            # the suit OR you can try to finesse a trick
            # OR if you're out of the suit and have a spade.
            #
            # If you're the last player in the hand, you can take the trick if you want (and can) using
            # the lowest winning card in your hand (or a spade if out).
            #
            # If you can't win the trick (you have one or more cards in the suit but none are greater
            # than the highest card already played), you can discard
            #

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
                if len(self.__outstanding_cards[suit_led]) > 0 and max_card_in_suit > self.__outstanding_cards[suit_led][-1]:
                    return Card(max_card_in_suit, suit_led)
                # otherwise, hold it in reserve and drop the lowest card if you can
                else:
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
            for i in range(4):
                if self.__card_count[i] > self.__potential_full_rounds[i] + 1:
                    have_lots_of_these_suits.append(i)
            long_suits = [Card.suits[s] for s in have_lots_of_these_suits]
            if long_suits != []:
                print('card count:', self.__card_count, 'potential full rounds:', self.__potential_full_rounds)
                print("have a lot of these suits:", long_suits)
            for i in range(4):
                if len(have_lots_of_these_suits) == 0 and i not in have_lots_of_these_suits:
                    if self.__outstanding_card_count[i] >= 2 and self.__card_count[i] == 2:
                        if self.__cards[i][-1] > self.__outstanding_cards[i][-1] and self.__cards[i][-2] < self.__outstanding_cards[i][-1]:
                            print("card drop to promote other card:", Card(self.__cards[i][0], i))
                            return Card(self.__cards[i][0], i)
            # otherwise, find the suit with the lowest loser card
            loser_suit = None
            loser_rank = 99
            for i in range(4):
                if len(self.__non_winners[i]) > 0:
                    if self.__non_winners[i][0] < loser_rank:
                        loser_rank = self.__non_winners[i][0]
                        loser_suit = i
            # print("discarding loser:", Card(loser_rank, loser_suit))
            if loser_suit is not None:
                return Card(loser_rank, loser_suit)
            # all cards are winners, so discard the lowest_winner
            if loser_suit is None:
                lowest_winner_suit = None
                lowest_winner_rank = 99
                for i in range(4):
                    if len(self.__potential_winners[i]) > 0:
                        if self.__potential_winners[i][0] < lowest_winner_rank:
                            lowest_winner_rank = self.__potential_winners[i][0]
                            lowest_winner_suit = i
            if lowest_winner_suit is not None:
                  # print("discarding lowest winner:", Card(lowest_winner_rank, lowest_winner_suit))
                  return Card(lowest_winner_rank, lowest_winner_suit)

        # BEGIN BODY OF play_card   #########################################################
        #

        
        self._hand.sort(key=lambda x: x.sort_key)
        # print("player", self."hand", self._hand, "hand copy", self._hand_copy)
        self.markup_status_of_cards_in_trick(trick)
        self.__arrange_cards__()

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
        if self.name == winner:
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
        Player.__init__(self, "Matthew")

class OCS_Team2(Player):
    def __init__(self):
        Player.__init__(self, "Mark")

class OCS_Team3(Player):
    def __init__(self):
        Player.__init__(self, "Luke")

class OCS_Team4(Player):
    def __init__(self):
        Player.__init__(self, "John")

