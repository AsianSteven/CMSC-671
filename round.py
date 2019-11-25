from player import Player, Card, Deck, OCS_Team1, OCS_Team2, OCS_Team3, OCS_Team4
import random
#import math
#import operator

# A class representing playing one round of 13 cards. Deals the cards, plays hands and
# maintains a count of tricks taken by player
#
class Round:
    # Initialization sets up the Players
    def __init__(self):
        self.suit_led = None
        self.cards_played = { 0: None, 1: None, 2: None, 3: None}
        self.trick = []
        self.number_of_players = 4
        self.player = []
        self.player.append(OCS_Team1())
        self.player.append(OCS_Team2())
        self.player.append(OCS_Team3())
        self.player.append(OCS_Team4())
        self.starting_player = None
        self.player_order = {
            0 : [0, 1, 2, 3],
            1 : [1, 2, 3, 0],
            2 : [2, 3, 0, 1],
            3 : [3, 0, 1, 2]
        }
        self.tricks_taken = [0, 0, 0, 0]
        
            
    # shuffle cards and deal them all out to the players
    def deal(self):
        self.deck = Deck()
        self.deck.shuffle()
        for idx, card in enumerate(self.deck.deck):
            self.player[idx%4].add_cards_to_hand([str(card)])
            if card == Card(0, 2):
                self.starting_player = idx%4

    # Utility for play_trick: add cards to the trick & cards_played variables
    def add_card(self, player, card_str):
        card = Card.create(card_str)
        self.cards_played[player] = card
        self.trick.append(card_str)
        if self.suit_led is None:
            self.suit_led = card.suit
        
    # 4 cards laid on the table and determines which card is the "winner". It will need to be
    # modified to take additional rules (like trump cards) into account.
    def play_trick(self, trick_no, starting_player):
        # initialize trick taking variables with each trick
        self.suit_led = None
        self.cards_played = { 0: None, 1: None, 2: None, 3: None}
        self.trick = []
        for idx, i in enumerate(self.player_order[self.starting_player]):
            self.add_card(self.player[i].playerID, self.player[i].play_card(self.player[i].get_name(), self.trick))
        # print("Winner of hand was player: ", self.trick.pick_winner())
        highest_card = -1
        winner = None
        trick = []
        # print(self.cards_played)
        for i in range(4):
            trick.append(str(self.cards_played[i]))
            if self.cards_played[i].suit == self.suit_led:
                if self.cards_played[i].rank > highest_card:
                    highest_card = self.cards_played[i].rank
                    highest_suit = self.suit_led
                    winner = i
        for i in range(4):
            self.player[i].collect_trick(round.player[i].get_name(), winner, trick)
        print("Winner of trick was:", self.player[winner].get_name(), 'with card', Card(highest_card, highest_suit))
        print("-------------------")
        return winner
        return self.trick.pick_winner()
     
    # play a hand (consists of 13 tricks)      
    def play_hand(self):
        # start each hand (round) and sets the starting player
        names = ['Matt', 'Mark', 'Luke', 'John']
        # calls the procedure to map names to agents and clean up data structures before
        # dealing
        for i in range(4):
            self.player[i].new_hand(names)
        self.deal()
        for i in range(13):
            self.starting_player = self.play_trick(i, self.starting_player)
            self.tricks_taken[self.starting_player] += 1
        print('Result of hand:')
        for i in range(4):
            print(self.player[i].get_name(), self.tricks_taken[i])
        print("-------------------")
        # print("Scores:", self.tricks_taken)


random.seed(30)
round = Round()
round.play_hand()
        



