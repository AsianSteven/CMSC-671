from card import Card
from deck import Deck
import math
import operator

# CUT-THROAT SPADES (no teams)
#
# AUTHOR: Wayne Nappari     DATE: 11/15/2019    Version 1
#
# Rules: 
# 1. A normal playing card deck consisting of 52 cards is dealt completely out to 4 players (13 cards/player)
# 2. Game play starts with the player who had the 2 of clubs, who plays that card. Each player selects and plays
#    one card (called a "trick").
# 3. Players must "follow suit" whenever they have a card in the suit led by whoever started the trick.
# 4. Winner of each trick is the person with the highest card in the suit (or highest trump card).
# 5. The winner of a trick gets to lead the next trick and can pick whatever card they want to play next.
#
# Based on current Piazza feedback, score is simply number of tricks without a penalty, so strategy is always
# aggressive and there is no need to consider sloughing off tricks to prevent overbids. This may change
# later in the project. Also, based on the in-class discussion of 11/14/2019, the first version should not include
# trumps (although later versions will now allow a user specified trump suit).
#
   

# Class representing the Player
class Player:
    def __init__(self, ID):
        self.playerID = ID
        self.name = "Organic Chem Survivors"
        self.hand = []
        self.hand_copy = []
        self.unseen_cards = {}
        self.cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.card_count = [0, 0, 0, 0]
        self.outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.outstanding_card_count = [0, 0, 0, 0]
        self.potential_full_rounds = [0, 0, 0, 0]
        self.bid = 0
        self.tricks_won = 0
        # represents knowledge about what cards this player has seen at any point.
        # before receiving your hand, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self.unseen_cards[card] = True

    # This function is called every time the agent is asked to play a card. It
    # splits the cards in the agent's hand and the remeaining outstanding (unseen)
    # cards into rank-ordered groups by suit. These variables make it easier to
    # make decisions in the code.
    def __arrange_cards__(self):
        self.cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.card_count = [0, 0, 0, 0]
        self.outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.outstanding_card_count = [0, 0, 0, 0]
        self.potential_winners = [ [], [], [], [] ]
        self.non_winners = [ [], [], [], [] ]
        for card in self.hand:
            self.cards[card.suit].append(card.rank)
        for card in self.unseen_cards:
            if self.unseen_cards[card]:
                self.outstanding_cards[card.suit].append(card.rank)
        for suit in range(4):
            self.cards[suit].sort()
            self.card_count[suit] = len(self.cards[suit])
            self.outstanding_cards[suit].sort()
            self.outstanding_card_count[suit] = len(self.outstanding_cards[suit])
            if self.card_count[suit] > 0:
                for j in range(self.card_count[suit]):
                    if self.outstanding_card_count[suit] > 0 and self.cards[suit][j] > self.outstanding_cards[suit][-1]:
                        self.potential_winners[suit].append(self.cards[suit][j])
                    else:
                        self.non_winners[suit].append(self.cards[suit][j])
            # print("winners:", potential_winners)
            # print("non-winners:", non_winners)

        #print("my card count", self.card_count, "outstanding card count:", self.outstanding_card_count)

    # Returns a string of the agent's name
    def get_name(self):
        return self.name

    # Returns a list of two character strings representing cards in the agent's hand
    def get_hand(self):
        return [str(c) for c in self.hand]

    # Takes a list of names of all agents in the game in clockwise order
    # and returns nothing. This method is also responsible for clearing any data
    # necessary for your agent to start a new round.
    def new_hand(self, names):
        self.names = names
        self.hand = []
        self.hand_copy = []
        self.unseen_cards = {}
        self.cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.card_count = [0, 0, 0, 0]
        self.outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.outstanding_card_count = [0, 0, 0, 0]
        self.potential_full_rounds = [0, 0, 0, 0]
        self.bid = 0
        self.tricks_won = 0
        # represents knowledge about what cards this player has seen at any point.
        # before receiving your hand, all cards are unseen...
        deck = Deck()
        for card in deck.deck:
            self.unseen_cards[card] = True
    
    # Takes a list of two character strings representing cards as an argument
    # and returns nothing.
    # This list can be any length.
    def add_cards_to_hand(self, cards):
        for c in cards:
            assert(len(c) == 2)
            rank = Card.ranks.index(c[0])
            suit = Card.suits.index(c[1])
            card = Card(rank, suit)
            self.hand.append(card)
            self.unseen_cards[card] = False
        
    
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

    # Takes a string of the name of the player who led the trick and
    # a list of cards in the trick "so far" as arguments.
    #
    # Returns a two character string from the agents hand of the card to be played
    # into the trick.
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
            # print("attempting to play: ", Card(rank, suit), "from hand:", self.hand)
            # print("player", self.playerID, "removing", Card(rank, suit))
            self.hand.remove(Card(rank, suit))
            # print("Player {0} played {1}".format(self.playerID, Card(rank, suit)))
            return Card.ranks[rank] + Card.suits[suit]

        # Pick a card to lead. Allows you to pick both the suit to lead and the card.
        def pick_a_card_to_lead_with():
            # Check for winners and play them
            for suit, rank in self.cards.items():
                # if you have a potential winner, play it...
                if self.card_count[suit] > 0:
                    # if all other players are out of the suit or it's the highest card still in the suit, play it
                    if self.outstanding_card_count[suit] == 0 or self.cards[suit][-1] > self.outstanding_cards[suit][-1]:
                        return Card(self.cards[suit][-1], suit)
            # Don't believe you have any winners right now, so pick another card.
            # Simple trategy at this point: Try to pick a the lowest card in a suit where you have at least
            # 2 cards with the hope you promote your other card to a winner...
            if self.card_count[Card.HEARTS] > 1 or self.card_count[Card.CLUBS] > 1 or self.card_count[Card.DIAMONDS] > 1 or self.card_count[Card.SPADES] > 1:
                # candidate suits are suits with more than 1 card
                candidates = [(self.cards[i][0], i) for i, j in enumerate(self.card_count) if j > 1]
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
                candidates = [(self.cards[i][0], i) for i, j in enumerate(self.card_count) if j > 0]
                # print("candidates check 2:", candidates)
                if len(candidates) > 0:
                    highest_rank, highest_suit = max(candidates, key=operator.itemgetter(0))
                    # print("returning 2:", Card(highest_rank, highest_suit))
                    return Card(highest_rank, highest_suit)

#        def pick_a_card_to_follow_suit(suit_led):
            #
            # If it's past the first turn (turns 2-4), you must follow suit if you can.
            # If you're in turns 2-3, you can try to take the trick if you have the highest card of
            # the suit OR you can try to finesse a trick (usually in spot 3)
            # OR if you're out of the suit and have a spade.
            #
            # If you're the last player in the hand, you can take the trick if you want (and can) using
            # the lowest winning card in your hand (or a spade if out).
            #
            # If you can't win the trick (you have one or more cards in the suit but none are greater
            # than the highest card already played), you can discard
            #

            # Quick shortcut. If you only have 1 card in the suit led, you must play it
#            print("suit led:", Card.suits[suit_led])
                                



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
                if self.card_count[i] > self.potential_full_rounds[i] + 1:
                    have_lots_of_these_suits.append(i)
            #print("have a lot of these suits:", [Card.suits[s] for s in have_lots_of_these_suits])
            for i in range(4):
                if len(have_lots_of_these_suits) == 0 and i not in have_lots_of_these_suits:
                    if self.outstanding_card_count[i] >= 2 and self.card_count[i] == 2:
                        if self.cards[i][-1] > self.outstanding_cards[i][-1] and self.cards[i][-2] < self.outstanding_cards[i][-1]:
                            # print("card drop to promote other card:", Card(self.cards[i][0], i))
                            return Card(self.cards[i][0], i)
            # otherwise, find the suit with the lowest loser card
            loser_suit = None
            loser_rank = 99
            for i in range(4):
                if len(self.non_winners[i]) > 0:
                    if self.non_winners[i][0] < loser_rank:
                        loser_rank = self.non_winners[i][0]
                        loser_suit = i
            # print("discarding loser:", Card(loser_rank, loser_suit))
            if loser_suit is not None:
                return Card(loser_rank, loser_suit)
            # all cards are winners, so discard the lowest_winner
            if loser_suit is None:
                lowest_winner_suit = None
                lowest_winner_rank = 99
                for i in range(4):
                    if len(self.potential_winners[i]) > 0:
                        if self.potential_winners[i][0] < lowest_winner_rank:
                            lowest_winner_rank = self.potential_winners[i][0]
                            lowest_winner_suit = i
            if lowest_winner_suit is not None:
                  # print("discarding lowest winner:", Card(lowest_winner_rank, lowest_winner_suit))
                  return Card(lowest_winner_rank, lowest_winner_suit)

        # BEGINNING OF BODY OF play_card        
                
        self.hand.sort(key=lambda x: x.sort_key)
        # print("player", self.playerID, "hand", self.hand, "hand copy", self.hand_copy)
        self.__arrange_cards__()
        # find highest card played in trick
        rank = -1
        # If no cards in the trick so far, it's the first time so you get to pick your own suit
        # as well as card to play.
        if len(trick) == 0:
            card = pick_a_card_to_lead_with()
            #print("picked card to lead was:", card)
            suit_led = card.suit
            return drop_card(card.rank, card.suit)
        else:
            suit_led = Card.create(trick[0]).suit
            # WARNING: Moving this into a procedure led to an unexpected, hard to trace error
            #          Probably a variable scope issue so do this later when you have time...
            # if you can follow suit, you must do so
            if len(self.cards[suit_led]) > 0:
                if len(self.cards[suit_led]) == 1:
                    return drop_card(self.cards[suit_led][0], suit_led)
 
                highest_card = highest_card_played_in_suit(suit_led, trick)
                # if the player has a card in the suit played, they must follow suit

                max_card_in_suit = self.cards[suit_led][-1]
                min_card_in_suit = self.cards[suit_led][0]
                # If you can't win, dump the lowest card in the suit
                if highest_card > max_card_in_suit:
                    return drop_card(min_card_in_suit, suit_led)
                else:
                    # Special logic for the last play of the trick. Basically, if you can win it,
                    # play the lowest winner...
                    if len(trick) == 3:
                        for i in range(self.card_count[suit_led]):
                            if self.cards[suit_led][i] > highest_card:
                                return drop_card(self.cards[suit_led][i], suit_led)
                    # otherwise, we should be in tricks 2 or 3 here
                    # if you have the highest card remaining, play it
                    if len(self.outstanding_cards[suit_led]) > 0 and max_card_in_suit > self.outstanding_cards[suit_led][-1]:
                        return drop_card(max_card_in_suit, suit_led)
                    # otherwise, hold it in reserve and drop the lowest card if you can
                    else:
                        return drop_card(min_card_in_suit, suit_led)
                    #pick_a_card_to_follow_suit(suit_led)
            # otherwise you must not have a card in the suit, so you must pick a card
            # (hopefully a losing card) from other suits to discard
            else:
                card = pick_a_non_led_card_to_discard()
                return drop_card(card.rank, card.suit)

                # I think I've taken care of all the cases here, so we should never get to this segment of code.
                # Hence, the assert(1==2) to toss us out to the OS if this ever happens
                assert(1==2) 
                values, new_suit = max(zip(self.cards.values(), self.cards.keys()))
                # print("suit chosen to discard:", Card.suits[new_suit], "had cards with ranks:", values)
                if new_suit is None:
                    print('failure finding new suit')
                min_card_in_suit = self.cards[new_suit][0]
                return drop_card(self.cards[new_suit][0], new_suit)
