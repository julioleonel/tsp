# importamos las librerías necesarias
import random
import json
import numpy
import matplotlib.pyplot as plt
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# data.json contiene el mapa de distancias (matriz de distancias entre puntos en formate JSON
with open("data.json", "r") as tsp_data:
    tsp = json.load(tsp_data)

# matriz de distancia
distance_map = tsp["DistanceMatrix"]

# numero de ciudades que visitar
IND_SIZE = tsp["TourSize"]

# Creamos los objetos para definir el problema y el tipo de individuo
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Generación de un Tour aleatorio
toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual, 100)


def evalTSP(individual):
    """Funcion objetivo, calcula la distancia que recorre el viajero"""
    # Distancia entre el ultimo elemento y el primero
    distance = distance_map[individual[-1]][individual[0]]
    # Distancia entre el resto de ciudades
    for gene1, gene2 in zip(individual[0:-1], individual[1:]):
        distance += distance_map[gene1][gene2]
    return distance,


# Registro de operaciones genéticas
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evalTSP)


def main():
    random.seed(100)
    CXPB, MUTPB, NGEN = 0.7, 0.3, 20
    pop = toolbox.population()
    MU, LAMBDA = len(pop), len(pop)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    logbook = tools.Logbook()
    pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats=stats, halloffame=hof)
    return hof, logbook


if __name__ == "__main__":
    best, log = main()
    best_individual = best[0]
    best_fitness = best_individual.fitness.values
    print("Mejor fitness: %f" % best_fitness)
    print("Mejor individuo: ", best)
