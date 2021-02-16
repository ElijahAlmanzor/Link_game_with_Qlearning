# config.py
#
# Configuration information for the Wumpus World. These are elements
# to play with as you develop your solution.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

# Dimensions in terms of the numbers of rows and columns
worldLength = 20
worldBreadth = 20

# Features
numberOfWumpus = 2
numberOfPits = 8
numberOfGold = 2

# Control dynamism
#
# If dynamic is True, then the Wumpus will move.
dynamic = False

# Control observability --- NOT YET IMPLEMENTED
#
# If partialVisibility is True, Link will only see part of the
# environment.
#Don't think this is actually used tbh
partialVisibility = True
#
# The limits of visibility when visibility is partial
sideLimit = 1
forwardLimit = 5

# Control determinism
#

# If nonDeterministic is True, Link's action model will be
# nonDeterministic. - uses the stochasticity of the functions
nonDeterministic = True
#
# If Link is nondeterministic, probability that they carry out the
# intended action:
directionProbability = 0.8

# Control images
#
# If useImage is True, then we use images for Link, Wumpus and
# Gold. If it is False, then we use simple colored objects.
useImage = True
