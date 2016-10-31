from enum import Enum, IntEnum
from random import uniform
from collections import defaultdict
import numpy as np
import numpy.linalg

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

  def __hash__(self):
    return hash((self.x, self.y))

class Compass(Enum):
  east = Position(0, 1)
  north = Position(-1, 0)
  west = Position(0, -1)
  south = Position(1, 0)

class Maze:
  def __init__(self, maze):
    self.height = len(maze)
    self.width = len(maze[0])
    for i in range(self.height):
      for j in range(self.width):
        if maze[i][j] == Tile.start:
          self.start = Position(i, j)
        elif maze[i][j] == Tile.end:
          self.end = Position(i, j)
    self.maze = maze
    self.create_markov()

  def look(self, position):
    return self.maze[position.x][position.y]

  def position_hash(self, position):
    total = 0
    for i, direction in enumerate(Compass):
      if self.look(position + direction.value) == Tile.block:
        total += 2 ** i
    return total

  def create_markov(self):
    open_id = {self.start: 0}
    current_id = 0
    for i in range(1, self.height - 1):
      for j in range(1, self.width - 1):
        pos = Position(i, j)
        if not (pos == self.start or pos == self.end) and self.look(pos) == Tile.open:
          current_id += 1
          open_id[pos] = current_id

    matrix = [['0' for _ in open_id] for _ in open_id]
    for pos, pid in open_id.items():
      surroundings = self.position_hash(pos)
      for i, direction in enumerate(Compass):
        new_pos = pos + direction.value
        if new_pos in open_id:
          newpid = open_id[new_pos]
          matrix[pid][newpid] = 'probs[%d][%d]' % (surroundings, i)

    self.markov = eval('lambda probs: ' + repr(matrix).replace("'", ''))

  def how_long(self, probs):
    Q = np.matrix(self.markov(probs))
    n = Q.shape[0]
    I = np.identity(n)
    try:
      return (np.linalg.solve(I - Q, np.ones((n, 1)))).item(0, 0)
    except np.linalg.linalg.LinAlgError:
      return np.inf

class Mouse:
  lifespan = 250

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

  def make_move(self, direction):
    new_pos = self.position + list(Compass)[direction].value
    self.position = new_pos

  def random_direction(self):
    surroundings = self.maze.position_hash(self.position)
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

    return total / N
