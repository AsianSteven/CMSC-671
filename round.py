from card import Card
from deck import Deck
import math
import operator

# CUT-THROAT SPADES (no teams)
#
# AUTHOR: Wayne Nappari     DATE: 11/11/2019
#
# Rules: 
# 1. A normal playing card deck consisting of 52 cards is dealt completely out to 4 players (13 cards/player)
# 2. Game play starts with the player who had the 2 of clubs, who plays that card. Each player selects and plays
#    one card (called a "trick").
# 3. Players must "follow suit" whenever they have a card in the suit led by whoever started the trick.
# 4. Winner of each trick is the person with the highest card in the suit (or highest trump card).
# 5. The winner of a trick gets to lead the next trick and can pick whatever card they want to play next (except
#    for spades, which cannot be led until spades have been broken (played on a trick as a trump card).
#
# Based on current Piazza feedback, score is simply number of tricks without a penalty, so strategy is always
# aggressive and there is no need to consider sloughing off tricks to prevent overbids. This may change
# later in the project...
   

# Class representing the Player
class Player:
    def __init__(self, ID):
        self.playerID = ID
        self.hand = []
        self.unseen_cards = {}
        self.cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.card_count = [0, 0, 0, 0]
        self.outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.outstanding_card_count = [0, 0, 0, 0]
        self.potential_full_rounds = [0, 0, 0, 0]
        self.bid = 0
        self.tricks_won = 0
        # represents knowledge about what cards this player has seen at any point
        deck = Deck()
        for card in deck.deck:
            self.unseen_cards[card] = True
           
    # split cards in hand by suit and order the individual suits by rank
    # also, does the same with outstanding (unseen) cards
    def __arrange_cards__(self):
        self.cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.card_count = [0, 0, 0, 0]
        self.outstanding_cards = {Card.SPADES: [], Card.HEARTS: [], Card.CLUBS: [], Card.DIAMONDS: []}
        self.outstanding_card_count = [0, 0, 0, 0]
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
        #print("my card count", self.card_count, "outstanding card count:", self.outstanding_card_count)

            
                
    def receive_card(self, card):
        self.hand.append(card)
        # when cards are dealt to the player, the status of cards flips to False
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
    
    def play_card(self, rank, suit, trick, turn, show_play = True):
        # does the trick contain any cards in the current suit?
        # if so, get the highest card
        def highest_card_played_in_suit(suit, trick):
            highest_rank = -1
            # self.cards_played = {0: None, 1: None, 2: None, 3: None}
            for i in range(4):
                if trick.cards_played[i] != None:
                    if trick.cards_played[i].suit == suit:
                        if trick.cards_played[i].rank > highest_rank:
                            highest_rank = trick.cards_played[i].rank
            return highest_rank

        def evaluate_hand(self, turn, bid, tricks_taken):
            # shortcut based on feedback in piazza...for simple game, score is just # of tricks
            # so there is no penalty, so just play flat-out aggressive...
            self.__arrange_cards__()
            return "take"
            # rest of function is dead code to be fixed up when more guidance is available
            # on the penalty for overages and the need to bid
##            others_unseen_cards = {}
##            expected_tricks = []
##            potential_full_rounds = [math.floor(x/3) for x in self.outstanding_card_count]
##            print("potential full rounds:", potential_full_rounds)
##
##            for suit in range(4):
##                # build a list of unseen cards arranged by suit and rank.
##                # others_unseen_cards[suit] = [k.rank for k, v in self.unseen_cards.items() if v and k.suit == suit]
##                # print("suit:", suit, "self.outstanding_cards:", self.outstanding_cards[suit], "others unseen cards:", others_unseen_cards[suit])
##                others_highest_card_ptr = -1
##
##                for i in reversed(self.cards[suit]):
##                        # If the cards suit is spades (the trump), count all solid potential winners
##                        tmp_unseen_cards_in_suit = list(self.outstanding_cards[suit])
##                        # SPADES: The relatively straightforward case....
##                        if suit == Card.SPADES:
##                            # If there are no outstanding spades, the card should be a winner
##                            if tmp_unseen_cards_in_suit == []:
##                                expected_tricks.append(Card(i, suit))
##                            else:
##                                # If this card is the highest card, it will be a winner
##                                if i > tmp_unseen_cards_in_suit[-1]:
##                                    expected_tricks.append(Card(i, suit)
##                                    for i in range(min(len(tmp_unseen_cards_in_suit), 3)):
##                                        del tmp_unseen_cards_in_suit[0]
##                                else:
##                                    del tmp_unseen_cards_in_suit[0]
##                        # NON-SPADES suits, the complex case
##                        else:
##                            # If there are enough cards for a complete round outstanding or spades are no
##                            # longer available to other players
##                            # Attempt 1: If there are enough cards for one or more suits, treat the suit
##                            # suit just like spades but only for the number of potential full rounds
##                            if self.outstanding_cards[Card.SPADES] != []:
##                                if potential_full_rounds[suit] > 0:
##                                    # If my card is the highest, expect it to be a winner
##                                    if i > tmp_unseen_cards_in_suit[-1]:
##                                        expected_tricks.append(Card(i, suit))
##                                        for i in range(min(len(tmp_unseen_cards_in_suit), 3)):
##                                            del tmp_unseen_cards_in_suit[0]
##                                    else:
##                                        del tmp_unseen_cards_in_suit[-1]
##                                    potential_full_rounds[suit] -=1
##                            else:
##                                if tmp_unseen_cards_in_suit == []:
##                                    if turn == 1:
##                                        expected_tricks.append(Card(i, suit))
##                                        for i in range(min(len(tmp_unseen_cards_in_suit), 3)):
##                                            del tmp_unseen_cards_in_suit[0]
##                                else:
##                                    # If this card is the highest card, it will be a winner
##                                    if i > tmp_unseen_cards_in_suit[-1]:
##                                        expected_tricks.append(Card(i, suit))
##                                        for i in range(min(len(tmp_unseen_cards_in_suit), 3)):
##                                            del tmp_unseen_cards_in_suit[0]
##                                    else:
##                                        del tmp_unseen_cards_in_suit[-1]
##            if expected_tricks != []:            
##                print("player", self.playerID, "hand was", self.hand, "and expected tricks: {0}".format([x for x in expected_tricks]))
##            
##            # if the tricks_taken plus number of expected tricks will exceed the bid, play to avoid taking tricks
##            if tricks_taken + len(expected_tricks) > bid:
##                return "avoid"
##            # else play to take more tricks
##            else:
##                return "take"
##    
        def drop_card(rank, suit, show_play = False):
            # since you're playing this card, remove it from your hand
            #print("attempting to play: ", Card(rank, suit))
            #print("player", self.playerID, "removing", Card(rank, suit))
            self.hand.remove(Card(rank, suit))
            # need to mark it as seen in every player's hand somehow
            for i in range(4):
                if i != self.playerID:
                    round.player[i].unseen_cards[Card(rank, suit)] = False
            if show_play:
                print("Player {0} played {1}".format(self.playerID, Card(rank, suit)))
            return Card(rank, suit)

        def pick_a_card_to_lead_with():
            # Check for winners and play them
            for suit, rank in self.cards.items():
            # if spades haven't been broken, skip over the suit
                if suit == Card.SPADES:
                    # if spades are broken and you have any spades...
                    if (round.spades_broken or (self.card_count[Card.HEARTS] == 0 and self.card_count[Card.CLUBS] == 0 and self.card_count[Card.DIAMONDS] == 0)) and self.card_count[suit] > 0:
                        # you can choose to lead a spade, if desired
                        spades_count = self.card_count[suit]
                        # if you have the highest rank spade, lead it to flush out spades
                        if self.outstanding_card_count[suit] == 0 or self.cards[suit][-1] > self.outstanding_cards[suit][-1]:
                            return Card(self.cards[suit][-1], suit)
                        else:
                            # if you have only SPADES, you must lead a spade so lead the lowest 
                            if self.card_count[Card.HEARTS] == 0 and self.card_count[Card.CLUBS] == 0 and self.card_count[Card.DIAMONDS] == 0:
                                return Card(self.cards[suit][0], suit)
                            # OR, if you have lots of spades, lead your lowest to flush out spades
                            elif self.card_count[suit] > self.potential_full_rounds[suit]:
                                return Card(self.cards[suit][0], suit)
                            # OTHERWISE, spades are valuable as trumps, so don't lead with them
                            else:
                                continue
                    else:
                        # spades haven't been broken, so can't lead a spade
                        continue
                else:
                     # if you have a potential winner, play it...
                     if self.card_count[suit] > 0:
                         if self.outstanding_card_count[suit] == 0 or self.cards[suit][-1] > self.outstanding_cards[suit][-1]:
                             return Card(self.cards[suit][-1], suit)
            # Don't believe you have any winners right now, so pick another card.
            # Strategy at this point: Try to pick a the lowest card in a suit where you have at least 2 cards
            #   with the hope you promote your other card to a winner...
            if self.card_count[Card.HEARTS] > 1 or self.card_count[Card.CLUBS] > 1 or self.card_count[Card.DIAMONDS] > 1:
                # candidate suits are non-spades with more than 1 card
                candidates = [(self.cards[i][0], i) for i, j in enumerate(self.card_count) if j > 1 and i != 0]
                print("candidates:", candidates)
                lowest_rank, lowest_suit = min(candidates, key=operator.itemgetter(1))
                return Card(lowest_rank, lowest_suit)
            # Late in the hand, you will have 1 or fewer cards in each trick
            else:
                # candidate suits are reduced to non-spades with just 1 card
                candidates = [(self.cards[i][0], i) for i, j in enumerate(self.card_count) if j == 1 and i != 0]
                print("candidates:", candidates)
                highest_rank, highest_suit = max(candidates, key=operator.itemgetter(0))
                return Card(highest_rank, highest_suit)

        # BEGINNING OF BODY OF play_card        
                
        # rank is only specified on the first card to play and you must play that card
        if rank == 0 and suit == Card.CLUBS:
            #evaluate_hand(self)
            return drop_card(rank, suit, show_play)
        # otherwise, here we choose the card to play
        else:
            self.hand.sort(key=lambda x: x.sort_key)
            # group the cards by suits and then order the rank to help make selection decisions
            strategy = evaluate_hand(self, turn, 13, round.tricks_taken[self.playerID])
            # find highest card played in trick
            rank = -1
            # print("trick turn:", turn)
            if turn == 1:
                card = pick_a_card_to_lead_with()
                print("picked card to lead was:", card)
                trick.suit_led = card.suit
                #return drop_card(card.rank, card.suit, show_play)
                                                           

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
            
            highest_card = highest_card_played_in_suit(trick.suit_led, trick)
            #print("highest card so far was: ", highest_card)

            #print(self.cards_by_suits)
            # if the player has a card in the suit played, they must follow suit
            if len(self.cards[trick.suit_led]) > 0:
                max_card_in_suit = self.cards[trick.suit_led][-1]
                min_card_in_suit = self.cards[trick.suit_led][0]
                # If you can't win, dump the lowest card in the suit
                if highest_card > max_card_in_suit:
                    return drop_card(min_card_in_suit, trick.suit_led, show_play)
                else:
                    # Special logic for the last play of the trick. Basically, if you can win it,
                    # play the lowest winner...
                    if turn == 4:
                        trick_was_trumped = False
                        for i in range(4):
                            if trick.cards_played[i] is not None and trick.cards_played[i].suit == Card.SPADES:
                                trick_was_trumped = True
                        if not trick_was_trumped:
                            for i in range(self.card_count[trick.suit_led]):
                                if self.cards[trick.suit_led][i] > highest_card:
                                    return drop_card(self.cards[trick.suit_led][i], trick.suit_led, show_play)
                    if self.outstanding_card_count[trick.suit_led] == 0 or max_card_in_suit > self.outstanding_cards[trick.suit_led][-1]:
                        return drop_card(max_card_in_suit, trick.suit_led, show_play)
                    else:
                        return drop_card(min_card_in_suit, trick.suit_led, show_play)
                    
            # if the player doesn't have a matching card in the suit
            else:
                # if you have a spade that's higher than the highest spade played, drop the lowest one
                if self.card_count[Card.SPADES] > 0:
                    highest_spade = -1
                    for i in range(4):
                        if trick.cards_played[i] is not None and trick.cards_played[i].suit == Card.SPADES and trick.cards_played[i].rank > highest_spade:
                            highest_spade = trick.cards_played[i].rank
                    for i in range(self.card_count[Card.SPADES]):
                        if self.cards[Card.SPADES][i] > highest_spade:
                            return drop_card(self.cards[Card.SPADES][i], Card.SPADES, show_play)
                        
                # pick suit with the most cards
                _, new_suit = max(zip(self.cards.values(), self.cards.keys()))
                
                if new_suit is None:
                    print('failure finding new suit')
                min_card_in_suit = self.cards[new_suit][0]
                return drop_card(min_card_in_suit, new_suit, show_play)

# 4 cards laid on the table and determines which card is the "winner". It will need to be
# modified to take additional rules (like trump cards) into account.
class Trick:
    def __init__(self):
        self.suit_led = None
        self.cards_played = {0: None, 1: None, 2: None, 3: None}

        
    def add_card(self, player, card):
        if card.suit == Card.SPADES:
            round.spades_broken = True
        self.cards_played[player] = card
        if self.suit_led is None:
            self.suit_led = card.suit
        elif card.suit != self.suit_led:
            round.player_out_of_suit[player][self.suit_led] = True
        
    def pick_winner(self):
        highest_card = -1
        trump_played = False
        winner = None
        for i in range(4):
            if self.cards_played[i].suit == Card.SPADES:
                if not trump_played:
                    highest_card = self.cards_played[i].rank
                    winner = i
                elif self.cards_played[i].rank > highest_card:
                    highest_card = self.cards_played[i].rank
                    trump_played = True
                    winner = i
            elif self.cards_played[i].suit == self.suit_led and not trump_played:
                if self.cards_played[i].rank > highest_card:
                    highest_card = self.cards_played[i].rank
                    highest_suit = self.suit_led
                    winner = i
        return winner
                
# A class representing playing one round of 13 cards. Deals the cards, plays hands and
# maintains a count of tricks taken by player
#
class Round:
    # Initialization sets up the Players
    def __init__(self):
        self.number_of_players = 4
        self.player = []
        self.starting_player = None
        self.player_order = {
            0 : [0, 1, 2, 3],
            1 : [1, 2, 3, 0],
            2 : [2, 3, 0, 1],
            3 : [3, 0, 1, 2]
        }
        self.tricks_taken = [0, 0, 0, 0]
        self.spades_broken = False
        self.player_out_of_suit = {
            0: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            1: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            2: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False},
            3: {Card.SPADES: False, Card.HEARTS: False, Card.CLUBS: False, Card.DIAMONDS: False}
        }
        for i in range(self.number_of_players):
            self.player.append(Player(i))
            
    # shuffle cards and deal them all out to the players
    def deal(self):
        self.deck = Deck()
        self.deck.shuffle()
        for idx, card in enumerate(self.deck.deck):
            self.player[idx%4].receive_card(card)
            if card == Card(0, 2):
                self.starting_player = idx%4
                
    # play one round (trick)
    def play_trick(self, trick_no, starting_player, suit):
        self.trick = Trick()
        for idx, i in enumerate(self.player_order[self.starting_player]):
            if trick_no == 0 and idx == 0:
                 self.trick.add_card(self.player[i].playerID, self.player[i].play_card(0, suit, self.trick, idx+1))
            else:
                self.trick.add_card(self.player[i].playerID, self.player[i].play_card(None, suit, self.trick, idx+1))
        print("Winner of hand was player: ", self.trick.pick_winner())
        return self.trick.pick_winner()
     
    # play a hand (consists of 13 tricks)      
    def play_hand(self):
        # start each hand (round) by resetting spades_broken to False
        self.deal()
        self.spades_broken = False        
        for i in range(13):
            self.starting_player = round.play_trick(i, self.starting_player, Card.CLUBS)
            self.tricks_taken[self.starting_player] += 1
            print("-------------------")
        print(self.tricks_taken)

round = Round()
round.play_hand()
        



