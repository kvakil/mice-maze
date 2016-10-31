# Mice Maze

This uses genetic programming to find an optimal solution to the ``mouse in the maze'' problem. (It currently works, but I'm still trying to find the best parameters.)

Here are the specifications:

* The mouse has no memory.
* The mouse can only see its direct surroundings.

At first, the problem seems impossible. Without memory, the mouse will simply get stuck in a loop. The key is to assign a probability to moving in each direction: a mouse which moves in a random direction will _eventually_ solve the maze. We can do better by exploiting patterns in the maze.

For example, consider the following maze:

    #########      S = start
    # # # #E#      E = end
    #S# # # #      # = wall
    #  1 2 3#      1, 2, 3 = labels, see below
    #########

Looking at squares (1) and (2), we see that the mouse should not go up because it would get stuck at deadends. At square (3), it should go up. The optimal mouse will distinguish between these two cases and avoid going up.

## Genetic Algorithm

The mouse's chromosome is a list of probabilities, which determines how likely it is to move in any direction given its surroundings. [DEAP](https://github.com/DEAP/deap) is used to implement the standard mu+lambda algorithm. 

## TODO

1. code cleanup and documentation.
2. full writeup.
