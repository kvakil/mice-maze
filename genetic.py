if __name__ == '__main__':
  from mice import *
  from deap import base, creator, tools, algorithms
  import numpy
  from numpy.random import dirichlet
  import random
  import argparse

  block_sizes = [4, 3, 3, 2, 3, 2, 2, 3, 2, 2, 2]

  def random_probs():
    probs = []
    for size in block_sizes:
      probs.extend(dirichlet(numpy.ones(size), size=1)[0])
    return probs

  def evaluate(individual, sims):
    m = Mouse(MAZE, individual)
    return m.simulate(sims),

  def mutate(individual):
    cur = 0
    for size in block_sizes:
      individual[cur:cur+size] = dirichlet(individual[cur:cur+size], size=1)[0]
      cur += size
    return (individual,)

  def mate(ind1, ind2, spread):
    weight = random.uniform(0.5 - spread, 0.5 + spread)
    for i in range(len(ind1)):
      ind1[i], ind2[i] = ind1[i] * weight + (1 - weight) * ind2[i], \
                         ind2[i] * weight + (1 - weight) * ind1[i]
    return ind1, ind2

  parser = argparse.ArgumentParser()
  parser.add_argument('maze', type=str,
                      help='file containing maze')
  parser.add_argument('--lifespan', default=250, type=int,
                      help='lifespan of each mouse (increase for longer mazes)')
  parser.add_argument('--spread', default=0.05, type=float,
                      help='variance for the mate')
  parser.add_argument('--sims', default=100, type=int,
                      help='number of times to simulate each mouse')
  parser.add_argument('--N', default=100, type=int,
                      help='number of mice in a generation')
  parser.add_argument('--mu', default=40, type=int,
                      help='mu parameter in mu+lambda EA')
  parser.add_argument('--lambda', default=60, type=int, dest='lambda_',
                      help='lambda parameter in mu+lambda EA')
  parser.add_argument('--cxpb', default=0.60, type=float,
                      help='crossover probability in EA')
  parser.add_argument('--mutpb', default=0.10, type=float,
                      help='mutation probability in EA')
  parser.add_argument('--ngen', default=50, type=int,
                      help='number of generations to run')
  parser.add_argument('--fame', default=5, type=int,
                      help='print the top FAME individuals')
  args = parser.parse_args()

  Mouse.lifespan = args.lifespan

  char_to_tile = {' ': Tile.open,
                  '#': Tile.block,
                  'S': Tile.start,
                  'E': Tile.end }
  with open(args.maze, 'r') as f:
    maze_array = [[char_to_tile[i] for i in line]
                                   for line in f.read().splitlines()]
  MAZE = Maze(maze_array)

  creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
  creator.create("Individual", list, fitness=creator.FitnessMin)

  toolbox = base.Toolbox()
  toolbox.register("individual", tools.initIterate, creator.Individual, random_probs)
  toolbox.register("population", tools.initRepeat, list, toolbox.individual)
  toolbox.register("mutate", mutate)
  toolbox.register("mate", mate, spread=args.spread)
  toolbox.register("select", tools.selBest)
  toolbox.register("evaluate", evaluate, sims=args.sims)

  stats = tools.Statistics(key=lambda ind: ind.fitness.values)
  stats.register("avg", numpy.mean)
  stats.register("stddev", numpy.std)
  stats.register("min", numpy.min)
  stats.register("max", numpy.max)

  hall = tools.HallOfFame(args.fame) if args.fame else None

  algorithms.eaMuPlusLambda(toolbox.population(n=args.N), toolbox, mu=args.mu,
                            lambda_=args.lambda_, cxpb=args.cxpb, mutpb=args.mutpb,
                            stats=stats, halloffame=hall, ngen=args.ngen)

  if hall:
    for individual in hall:
      print(Mouse(MAZE, individual).probs)
