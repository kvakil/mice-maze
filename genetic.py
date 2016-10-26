if __name__ == '__main__':
  from mice import *
  from deap import base, creator, tools, algorithms
  import numpy as np
  from numpy.random import dirichlet
  import random

  maze = [[Tile.block, Tile.block, Tile.block, Tile.block, Tile.block, Tile.block],
          [Tile.block, Tile.start, Tile.block, Tile.end  , Tile.open,  Tile.block],
          [Tile.block, Tile.open , Tile.open , Tile.block, Tile.open , Tile.block],
          [Tile.block, Tile.open , Tile.block, Tile.open , Tile.open , Tile.block],
          [Tile.block, Tile.open , Tile.open , Tile.open , Tile.open , Tile.block],
          [Tile.block, Tile.block, Tile.block, Tile.block, Tile.block, Tile.block]]

  MAZE = Maze(maze)

  block_sizes = [4, 3, 3, 2, 3, 2, 2, 3, 2, 2, 2]
  def random_probs():
    probs = []
    for size in block_sizes:
      probs.extend(dirichlet(np.ones(size), size=size)[0])
    return probs

  def evaluate(individual):
    m = Mouse(MAZE, individual)
    return m.simulate(100),

  def mutate(individual):
    cur = 0
    for size in block_sizes:
      for j in range(size):
        individual[cur + j] += 0.1 * random.random()
      total = sum(individual[cur:cur+size])
      individual[cur:cur+size] = [e / total for e in individual[cur:cur+size]]
      cur += size
    return (individual,)

  creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
  creator.create("Individual", list, fitness=creator.FitnessMin)

  GENOME = 28

  toolbox = base.Toolbox()
  toolbox.register("individual", tools.initIterate, creator.Individual, random_probs)
  toolbox.register("population", tools.initRepeat, list, toolbox.individual)
  toolbox.register("mutate", mutate)
  toolbox.register("mate", tools.cxUniform, indpb=0.10)
  toolbox.register("select", tools.selBest)
  toolbox.register("evaluate", evaluate)

  stats = tools.Statistics(key=lambda ind: ind.fitness.values)
  stats.register("avg", np.mean)
  stats.register("std", np.std)
  stats.register("min", np.min)
  stats.register("max", np.max)

  hall = tools.HallOfFame(5)

  algorithms.eaMuPlusLambda(toolbox.population(n=100), toolbox, mu=40, lambda_=60,
                            cxpb=0.20, mutpb=0.30, stats=stats, halloffame=hall, ngen=50)

  import pprint
  for individual in hall:
    pprint.pprint(Mouse(MAZE, individual).probs)
