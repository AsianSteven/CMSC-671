from round import Round

# CUT-THROAT SPADES (no teams)
#
# AUTHOR: Wayne Nappari     DATE: 11/24/2019
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

class Game:
    def __init__(self):
        self.tricks_taken = [0, 0, 0, 0]
        self.round = Round()

    def play_game(self, cutoff):
        winner = []
        top_score = 0
        while top_score < cutoff:
            self.round.tricks_taken = [0, 0, 0, 0]
            self.round.play_hand()
            self.tricks_taken = [self.tricks_taken[i]+self.round.tricks_taken[i] for i in range(4)]
            top_score = max(self.tricks_taken)
        print("Final scores were", self.tricks_taken)
        for i in range(4):
            if self.tricks_taken[i] == top_score:
                winner.append(self.round.player[i].playerID)
        if len(winner) > 1:
            print("Winner list was", winner, "There was a tie. The winners are:", winner)
        else:
            print("Winner list was", winner, "The winner is", winner)
                
game = Game()
game.play_game(1000)




