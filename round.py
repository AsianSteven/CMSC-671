from card import Card
from deck import Deck
from player import Player
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
   

# 4 cards laid on the table and determines which card is the "winner". It will need to be
# modified to take additional rules (like trump cards) into account.
class Trick:
    def __init__(self):
        self.suit_led = None
        self.cards_played = {0: None, 1: None, 2: None, 3: None}
        self.trick = []
        
    def add_card(self, player, card_str):
        #print("card_str was:", card_str)
        card = Card.create(card_str)
        self.cards_played[player] = card
        self.trick.append(card_str)
        if self.suit_led is None:
            self.suit_led = card.suit
#        elif card.suit != self.suit_led:
#            Round.player_out_of_suit[player][self.suit_led] = True
        
    def pick_winner(self):
        highest_card = -1
        winner = None
        # print(self.cards_played)
        for i in range(4):
            if self.cards_played[i].suit == self.suit_led:
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
            self.player[idx%4].add_cards_to_hand([str(card)])
            if card == Card(0, 2):
                self.starting_player = idx%4
                
    # play one round (trick)
    def play_trick(self, trick_no, starting_player):
        self.trick = Trick()
        for idx, i in enumerate(self.player_order[self.starting_player]):
            self.trick.add_card(self.player[i].playerID, self.player[i].play_card(self.player[i].get_name(), self.trick.trick))
        # print("Winner of hand was player: ", self.trick.pick_winner())
        return self.trick.pick_winner()
     
    # play a hand (consists of 13 tricks)      
    def play_hand(self):
        # start each hand (round) and sets the starting player
        names = ['Matthew', 'Mark', 'Luke', 'John']
        for i in range(4):
            self.player[i].new_hand(names)
        self.deal()
        for i in range(4):
            self.player[i].hand_copy = self.player[i].hand.copy()
            self.player[i].hand_copy.sort(key=lambda x: x.sort_key)
        for i in range(13):
            self.starting_player = self.play_trick(i, self.starting_player)
            self.tricks_taken[self.starting_player] += 1
            # print("-------------------")
        # print("Scores:", self.tricks_taken)
        for i in range(4):
            print("{0},{1}".format(self.player[i].hand_copy, self.tricks_taken[i]))

#round = Round()
#round.deal()
#for i in range(4):
#    print("Team:", round.player[i].get_name(), "hand:", round.player[i].get_hand())
#round.play_hand()
        



