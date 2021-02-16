# link.py
#
# The code that defines the behaviour of Link. You should be able to
# do all you need in here, using access methods from world.py, and
# using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

from world import World
import random
import utils
from utils import Directions
import numpy as np
import config
#from game import gameWorld
#imported the world just to be able to test my code
#gameWorld = World()


#For testing the Link code without starting the game itself
gw = World(1,1,2, 10)


class Link():

    def __init__(self, dungeon, q_map):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        self.dp = config.directionProbability
        self.side_dp = 1.0-self.dp

        self.Q_map = q_map

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Link
        # directly towards the gold.
        # 
        # Get the location of the gold.
        allGold = self.gameWorld.getGoldLocation()
        if len(allGold) > 0:
            nextGold = allGold[0]
        myPosition = self.gameWorld.getLinkLocation()


        # If not at the same x coordinate, reduce the difference --> east is to the right
        if nextGold.x > myPosition.x:
            return Directions.EAST
        if nextGold.x < myPosition.x:
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if nextGold.y > myPosition.y:
            return Directions.NORTH
        if nextGold.y < myPosition.y:
            return Directions.SOUTH

    def max_from_utility(self, u_map, x, y):

        #Prevents over-indexing the utility map
        #For indexing the states adjacent to the current state
        n_x_to_west = -1
        n_x_to_east = 1
        n_y_to_north = 1
        n_y_to_south = -1

        #if state is at x == 0, then can only move east (right) and not west (left)
        if x == 0:
            n_x_to_west = 0
        #likewise if x coordinate is at end, then can only move west (left)
        elif x == (config.worldBreadth-1):
            n_x_to_east = 0

        #same as above but for the y direction
        if y == 0:
            n_y_to_south = 0

        elif y == (config.worldLength-1):
            n_y_to_north = 0
        
        #Action of going to North (as expected)
        NORTH = u_map[y+n_y_to_north][x]*self.dp + u_map[y][x+n_x_to_west]*self.side_dp/2 + u_map[y][x+n_x_to_east]*self.side_dp/2
        #Action of going South
        SOUTH = u_map[y+n_y_to_south][x]*self.dp + u_map[y][x+n_x_to_west]*self.side_dp/2 + u_map[y][x+n_x_to_east]*self.side_dp/2
        #Action of going East
        EAST = u_map[y][x+n_x_to_east]*self.dp + u_map[y+n_y_to_north][x]*self.side_dp/2 + u_map[y+n_y_to_south][x]*self.side_dp/2
        #West
        WEST = u_map[y][x+n_x_to_west]*self.dp + u_map[y+n_y_to_north][x]*self.side_dp/2 + u_map[y+n_y_to_south][x]*self.side_dp/2
        
        #North is index 0, South is 1, East is 2, and west is 3
        action_list = [NORTH, SOUTH, EAST, WEST]
 
        #choose the max expected out of all the actions
        max_expected_action = max(action_list)

        #Index of which action has max expected
        which_action = action_list.index(max_expected_action)
        #print(action_list)
        #print(which_action)
        #returns the max value as well as the action that gave that max value and the list (was used for error checking)
        return (max_expected_action, which_action, action_list)   


    def util_map(self):

        
            #Definition of constants for iterative Bellman Equation
            gamma = 0.9
            reward_empty = -0.04
            reward_gold = 1.0
            #reward_get_away = 0.5
            reward_pits = -1
            reward_wumpus = -1
            reward_forward_wumpus = -1
            
            #Obtain gold locations
            gold_coord = list()
            for i in range(len(self.gameWorld.getGoldLocation())):
                    coord = (self.gameWorld.getGoldLocation()[i].x,self.gameWorld.getGoldLocation()[i].y)
                    gold_coord.append(coord)
            
            #print(gold_coord)

            #Obtain pits locations
            pits_coord = list()
            for i in range(len(self.gameWorld.getPitsLocation())):
                    coord = (self.gameWorld.getPitsLocation()[i].x,self.gameWorld.getPitsLocation()[i].y)
                    pits_coord.append(coord)

            #Obtain Wumpus locations
            wumpus_coord = list()
            for i in range(len(self.gameWorld.getWumpusLocation())):
                    coord = (self.gameWorld.getWumpusLocation()[i].x,self.gameWorld.getWumpusLocation()[i].y)
                    wumpus_coord.append(coord)

            #2D utility map (array) that stores all the utiliies for every state (x,y coordinates)
            #Using worldBreadth in the X direction and worldLength in the Y direction
            #Initially just values of zero
            utility_map = np.zeros((config.worldBreadth, config.worldLength))

            #Numerical iteration of the Bellman equations
            #Loops until a breakout condition has been satisfied
            while 1:
                #Make copy of utility map for the while loops
                #Important that it was converted to list to allow for indexing operations without messing up their values
                utility_map_copy = utility_map.tolist()
                
                #This bit iterates through every state in the utility map
                for x in range(config.worldBreadth):
                    for y in range(config.worldLength):

                        #Fix the values for final end-states as their reward values
                        if (x,y) in gold_coord:
                            utility_map[y][x] = reward_gold 
                            continue
                            
                        elif (x,y) in pits_coord:
                            utility_map[y][x] = reward_pits
                            continue

                        elif (x,y) in wumpus_coord:
                            utility_map[y][x] = reward_wumpus

                            link_coord = (self.gameWorld.getLinkLocation().x, self.gameWorld.getLinkLocation().y)

                            #If statement to make link more likely to avoid the next positions of the wumpus
                            if link_coord[0] > x:
                                utility_map[y][x+1] = reward_forward_wumpus
                            elif link_coord[0] < x:
                                utility_map[y][x-1] = reward_forward_wumpus

                            if link_coord[1] > y:
                                utility_map[y+1][x] = reward_forward_wumpus
                            elif link_coord[1] < y: 
                                utility_map[y-1][x] = reward_forward_wumpus

                            
                            
                            #print(self.gameWorld.linkSmelly())
                            '''
                            if self.gameWorld.linkSmelly():
                                #Technically don't need the linkSmelly if but makes the code look a little bit nicer

                                #Make the probability of link moving away from the wumpus in the x-direction higher
                                if x == link_coord[0]+1 and link_coord[0] != 0:
                                    utility_map[y][x-1] = reward_get_away
                                elif x == link_coord[0]-1 and link_coord[0] != config.worldBreadth-1:
                                    utility_map[y][x+1] = reward_get_away

                                #Same as above, but in the y-direction
                                if y == link_coord[1]+1 and link_coord[1] != 0:
                                    utility_map[y-1][x] = reward_get_away
                                elif y == link_coord[1]-1 and link_coord[1] != config.worldLength-1:
                                    utility_map[y+1][x] = reward_get_away
                            '''
                            continue

                        else:
                            #If the current state is just an empty x,y coordinate
                            cur_reward = reward_empty
                        
                        #Use the previous iterations utility map to work out the next iterations utility map for the current state
                        max_action_utility = self.max_from_utility(utility_map_copy, x, y)

                        #x,y has to be switched to y,x due to how numpy arrays are indexed (the axes are flipped)
                        #doesn't really matter but made printing utility map values more in line with the game map
                        utility_map[y][x] = cur_reward + gamma*(max_action_utility[0])
                        
                #If the max index difference between the current iteration and previous iterations utility maps is less than a small value
                #Break out of the while loop
                if abs(np.amax(utility_map - np.array(utility_map_copy))) < 0.001:
                    break
                
            #print(utility_map)
            return utility_map



    def q_Move(self):
        #Function for holdign the iterative Q values

        gamma = 0.9
        alpha = 0.4
        reward_empty = -0.04
        reward_gold = 1.0
        reward_pits = -1
        reward_wumpus = -1
        
        #Obtain gold locations
        gold_coord = list()
        for i in range(len(self.gameWorld.getGoldLocation())):
                coord = (self.gameWorld.getGoldLocation()[i].x,self.gameWorld.getGoldLocation()[i].y)
                gold_coord.append(coord)
        
        #print(gold_coord)

        #Obtain pits locations
        pits_coord = list()
        for i in range(len(self.gameWorld.getPitsLocation())):
                coord = (self.gameWorld.getPitsLocation()[i].x,self.gameWorld.getPitsLocation()[i].y)
                pits_coord.append(coord)

        #Obtain Wumpus locations
        wumpus_coord = list()
        for i in range(len(self.gameWorld.getWumpusLocation())):
                coord = (self.gameWorld.getWumpusLocation()[i].x,self.gameWorld.getWumpusLocation()[i].y)
                wumpus_coord.append(coord)

        #uses the current state (as the select a random strate)
        link_coord = (self.gameWorld.getLinkLocation().x, self.gameWorld.getLinkLocation().y)

        #CHOOSE A RANDOM ACTION
        n_x_to_west = -1
        n_x_to_east = 1
        n_y_to_north = 1
        n_y_to_south = -1

        #if state is at x == 0, then can only move east (right) and not west (left)
        if link_coord[0] == 0:
            n_x_to_west = 0
        #likewise if x coordinate is at end, then can only move west (left)
        elif link_coord[0] == (config.worldBreadth-1):
            n_x_to_east = 0

        #same as above but for the y direction
        if link_coord[1] == 0:
            n_y_to_south = 0

        elif link_coord[1] == (config.worldLength-1):
            n_y_to_north = 0
        
        #Action of going to North (as expected)

        NORTH = (link_coord[0], link_coord[1] + n_y_to_north)
        SOUTH = (link_coord[0], link_coord[1] - n_y_to_south)
        EAST = (link_coord[0] + n_x_to_east, link_coord[1])
        WEST = (link_coord[0] + n_x_to_west, link_coord[1])
        
        #reach the next state
        action_choice = [NORTH, SOUTH, EAST, WEST]
        action = random.choice(range(len(action_choice)))
        next_state = action_choice[action]


        #Get the reward
        if next_state in gold_coord:
            reward = reward_gold 
                            
        elif next_state in pits_coord:
            reward = reward_pits

        elif next_state in wumpus_coord:
            reward = reward_wumpus

        else:
            #If the current state is just an empty x,y coordinate
            reward = reward_empty

        #Q_next_state at t
        Q_next_state = self.Q_map[next_state[0]][next_state[1]]


        #Compute the temporal difference

        #if state is at x == 0, then can only move east (right) and not west (left)
        if next_state [0] == 0:
            n_x_to_west = 0
        #likewise if x coordinate is at end, then can only move west (left)
        elif next_state [0] == (config.worldBreadth-1):
            n_x_to_east = 0

        #same as above but for the y direction
        if next_state [1] == 0:
            n_y_to_south = 0
        elif next_state [1] == (config.worldLength-1):
            n_y_to_north = 0

        
        #fully deterministic atm
        NORTH_t_1 = self.Q_map[next_state[0]][next_state[1] + n_y_to_north]
        SOUTH_t_1 = self.Q_map[next_state[0]][next_state[1] - n_y_to_south]
        EAST_t_1 = self.Q_map[link_coord[0]][n_x_to_east + next_state[1]]
        WEST_t_1 = self.Q_map[link_coord[0]][n_x_to_west + next_state[1]]
        Q_next_state_t_1 = max([NORTH_t_1, SOUTH_t_1, EAST_t_1, WEST_t_1])

        #Temporal difference equation
        TD = reward + gamma*Q_next_state_t_1 - Q_next_state
        self.Q_map[next_state[0]][next_state[1]] = Q_next_state + alpha*TD
                    
        #Now to actually update link
        return self.moves[action]

    def updateQmap(self):
        return self.Q_map

    def move_after_Q_learn(self):
        obtained_q_map = self.Q_map
        link_coord = (self.gameWorld.getLinkLocation().x, self.gameWorld.getLinkLocation().y)
        greedy_action = self.max_from_utility(obtained_q_map, link_coord[0], link_coord[1])
        return self.moves[greedy_action[1]]


    def my_makeMove(self):

        #Function to make Link move by using greedy choice from the iteratively found max utility map
        #Work out utility map every iteration in case anything has changed (e.g. taken gold, Wumpus' have moved)
        current_utility_map = self.util_map().tolist()
        
        #Get links current location.
        link_coord = (self.gameWorld.getLinkLocation().x, self.gameWorld.getLinkLocation().y)

        #Force the Gold loction to update as sometimes it doesn't delete the image
        self.gameWorld.getGoldLocation()


        #Print the best policy for each state
        '''
        for x in range(config.worldBreadth):
                    for y in range(config.worldLength):
                        print("For state:")
                        print((x,y))
                        greedy_action = self.max_from_utility(current_utility_map, x, y)
                        print("The best policy is:")
                        print(self.moves[greedy_action[1]])
        '''

        #Now to choose which action would be best - based on a greedy choice/policy of the current best utilities
        greedy_action = self.max_from_utility(current_utility_map, link_coord[0], link_coord[1])


        #Prints the best action for viewing in the terminal
        #print(self.moves[greedy_action[1]])

        #returns the calculated next move back to game.py
        return self.moves[greedy_action[1]]




    


    

if __name__ == "__main__":
    link = Link(gw)
    #link.util_map()


    link.my_makeMove()
   # Link(self.gameWorld).my_makeMove()
    #utils.printGameState(gameWorld)