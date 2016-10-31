if __name__ == '__main__':
  from mice import *
  from deap import base, creator, tools, algorithms
  import numpy
  from numpy.random import dirichlet
  import random
  import argparse

  block_sizes = [4, 3, 3, 2, 3, 2, 2, 3, 2, 2, 2]
  GENOME_SIZE = sum(block_sizes)

  def evaluate(individual, sims):
    m = Mouse(MAZE, individual)
    return MAZE.how_long(m.probs),

  def mutate(individual):
    cur = 0
    for size in block_sizes:
      individual[cur:cur+size] = dirichlet(individual[cur:cur+size], size=1)[0]
      cur += size
    return (individual,)

  def random_probs():
    return mutate(numpy.ones(GENOME_SIZE))[0]

  def mate(ind1, ind2, spread):
    weight = 0.5 + random.uniform(-spread, spread) / 2
    for i in range(GENOME_SIZE):
      ind1[i], ind2[i] = ind1[i] * weight + (1 - weight) * ind2[i], \
                         ind2[i] * weight + (1 - weight) * ind1[i]
    return ind1, ind2


  def nonnegative(val):
    val = int(val)
    if val < 0:
      raise argparse.ArgumentTypeError("%s must be nonnegative" % val)
    return val

  def probability(val):
    val = float(val)
    if not (0 <= val <= 1):
      raise argparse.ArgumentTypeError("%s must be between 0 and 1" % val)
    return val

  parser = argparse.ArgumentParser()
  parser.add_argument('maze', type=str,
                      help='file containing maze')
  parser.add_argument('--lifespan', default=250, type=nonnegative,
                      help='lifespan of each mouse (increase for longer mazes)')
  parser.add_argument('--spread', default=0.10, type=probability,
                      help='variance for the mate')
  parser.add_argument('--sims', default=100, type=nonnegative,
                      help='number of times to simulate each mouse')
  parser.add_argument('--N', default=100, type=nonnegative,
                      help='number of mice in a generation')
  parser.add_argument('--mu', default=40, type=nonnegative,
                      help='mu parameter in mu+lambda EA')
  parser.add_argument('--lambda', default=60, type=nonnegative, dest='lambda_',
                      help='lambda parameter in mu+lambda EA')
  parser.add_argument('--cxpb', default=0.60, type=probability,
                      help='crossover probability in EA')
  parser.add_argument('--mutpb', default=0.10, type=probability,
                      help='mutation probability in EA')
  parser.add_argument('--ngen', default=50, type=nonnegative,
                      help='number of generations to run')
  parser.add_argument('--fame', default=1, type=nonnegative,
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
      print(Mouse(MAZE, individual).simulate(args.sims))
