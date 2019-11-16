SPADES
Wayne Nappari
11/19/2019

Stripped down version of the spades code to eliminate trump usage and refactor most
of the way to the TA's framework.

Changed the print statements to make it print only sorted hands followed by the
number of tricks. Currently set up to run 1000 hands (so 4000 training hands), but
that ran in less than 5 seconds on my PC. Just redirect the output to a file to collect
a set of training data.

This is probably not helpful, but if you think about the entries produced, every 4
lines are hands that played against each other. It probably isn't helpful because in the
real play environment, none of the agents actually know what the other agents have. They
only know what they have in their own hand and what the result of playing the hand is.
That's pretty much what you get in the output.

You can get lots more output by changing the range limit in the for statement in the
play_game function of the Game class. Basically as much as you have the patience to produce.

This current version uses only a lose set of heuristics to play the game, not a solid
set. I'll play with making the heuristics a little more solid to help with whatever AI
approach we use. If machine learning, it'll give better training data. Otherwise it might
serve to put constraints on the actions you need to explore in a min-max tree.
