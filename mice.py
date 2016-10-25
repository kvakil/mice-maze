from enum import Enum, IntEnum
from random import uniform

class Tile(Enum):
  open = 0
  block = 1
  start = 2
  end = 3

class Position:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __add__(self, other):
    return Position(self.x + other.x, self.y + other.y)

  def __repr__(self):
    return "Position({0}, {1})".format(self.x, self.y)

  def __str__(self):
    return "({0}, {1})".format(self.x, self.y)

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

  def __ne__(self, other):
    return self.x != other.x or self.y != other.y

class Compass(Enum):
  east = Position(0, 1)
  north = Position(-1, 0)
  west = Position(0, -1)
  south = Position(1, 0)

class Maze:
  def __init__(self, maze):
    for i in range(len(maze)):
      for j in range(len(maze[i])):
        if maze[i][j] == Tile.start:
          self.start = Position(i, j)
          maze[i][j] = Tile.open
        elif maze[i][j] == Tile.end:
          self.end = Position(i, j)
          maze[i][j] = Tile.open
    self.maze = maze

  def look(self, position):
    return self.maze[position.x][position.y]

class Mouse:
  lifespan = 200

  def __init__(self, maze, probs):
    self.probs = [[probs[ 0], probs[ 1], probs[ 2], probs[ 3]], # ENWS
                  [0        , probs[ 4], probs[ 5], probs[ 6]], #  NWS
                  [probs[ 7], 0        , probs[ 8], probs[ 9]], # E WS
                  [0        , 0        , probs[10], probs[11]], #   WS
                  [probs[12], probs[13], 0        , probs[14]], # EN S
                  [0        , probs[15], 0        , probs[16]], #  N S
                  [probs[17], 0        , 0        , probs[18]], # E  S
                  [0        , 0        , 0        , 1        ], #    S
                  [probs[19], probs[20], probs[21], 0        ], # ENW 
                  [0        , probs[22], probs[23], 0        ], #  NW 
                  [probs[24], 0        , probs[25], 0        ], # E W 
                  [0        , 0        , 1        , 0        ], #   W 
                  [probs[26], probs[27], 0        , 0        ], # EN  
                  [0        , 1        , 0        , 0        ], #  N  
                  [1        , 0        , 0        , 0        ]] # E   
    self.maze = maze
    self.position = maze.start
    self.turns = 0

  def look_around(self):
    right = self.position + Compass.east.value
    up = self.position + Compass.north.value
    left = self.position + Compass.west.value
    down = self.position + Compass.south.value
    return 1 * self.maze.look(right).value + \
           2 * self.maze.look(up).value + \
           4 * self.maze.look(left).value + \
           8 * self.maze.look(down).value

  def make_move(self, direction):
    new_pos = self.position + list(Compass)[direction].value
    self.position = new_pos

  def random_direction(self):
    surroundings = self.look_around()
    cdf = uniform(0, 1)
    i = 0
    while cdf > 0 and i < 4:
      cdf -= self.probs[surroundings][i]
      i += 1

    # roundoff error: return the most likely move
    if cdf > 0:
      return max(range(4), key=lambda idx: self.probs[surroundings][idx])

    return i - 1

  def step(self):
    self.turns += 1
    self.make_move(self.random_direction())

  def simulate(self, N):
    total = 0
    for i in range(N):
      while self.position != self.maze.end and self.turns < Mouse.lifespan:
        self.step()

      total += self.turns

      self.turns = 0
      self.position = self.maze.start

    return total/N

