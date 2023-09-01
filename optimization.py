import json
import random
import numpy as np

# data.json contiene el mapa de distancias (matriz de distancias entre puntos en formato JSON)
with open("data.json", "r") as tsp_data:
    tsp = json.load(tsp_data)

# Datos del problema
distance_matrix = tsp["DistanceMatrix"]

# Define los nodos de inicio y final, así como los nodos intermedios
start_node = 1
end_node = 7
intermediate_nodes = [0, 3, 5]

# Parámetros del algoritmo genético
population_size =10
generations = 10
crossover_prob = 0.7
mutation_prob = 0.3
num_runs = 5  # Número de ejecuciones del algoritmo

# Calcula el mínimo y el máximo de la longitud del recorrido permitido
min_tour_size = len(intermediate_nodes) + 2  # Mínimo requerido
max_tour_size = len(distance_matrix) - 1  # Máximo posible


# Función para generar una población inicial aleatoria
def generate_population(population_size, min_tour_size, max_tour_size, start_node, end_node, intermediate_nodes):
    population = []
    for _ in range(population_size):
        # Asegura que el tamaño del recorrido no sea mayor que el número total de nodos
        tour_size = min(random.randint(min_tour_size, max_tour_size), len(distance_matrix))
        individual = [start_node] + random.sample(intermediate_nodes, len(intermediate_nodes)) + [end_node]

        # Ajusta la longitud del individuo si es necesario
        if tour_size < len(individual):
            individual = individual[:tour_size]
        elif tour_size > len(individual):
            remaining_nodes = [node for node in range(len(distance_matrix)) if node not in individual]
            random.shuffle(remaining_nodes)
            individual = individual[:1] + remaining_nodes[:tour_size - len(individual)] + individual[1:]

        population.append(individual)

    return population


def evaluate_restrictions(individual):
    # Verifica que el individuo tenga los nodos extremos indicados y que tenga como mínimo los nodos intermedios también indicados
    if individual[0] == start_node and individual[-1] == end_node and set(intermediate_nodes).issubset(set(individual)):
        # Verifica que no haya nodos repetidos consecutivos
        for i in range(len(individual) - 1):
            if individual[i] == individual[i + 1]:
                return False
        return True
    else:
        return False



# Función para calcular la aptitud de un individuo (distancia total del recorrido)
def evaluate_individual(individual, distance_matrix):
    distance = 0
    for i in range(len(individual) - 1):
        from_node = individual[i]
        to_node = individual[i + 1]
        distance += distance_matrix[from_node][to_node]
    return distance


# Función de selección (torneo)
def select(population, k):
    selected = []
    for _ in range(k):
        if len(population) < 2:
            # Si la población tiene menos de 2 individuos, selecciona uno al azar
            selected.append(random.choice(population))
        else:
            tournament = random.sample(population, 2)
            winner = min(tournament, key=lambda individual: evaluate_individual(individual, distance_matrix))
            selected.append(winner)
    return selected


# Función de cruce (crossover)
def crossover(parent1, parent2):
    if len(parent1) != len(parent2):
        # Si los padres tienen diferentes longitudes, simplemente devuelve los mismos padres
        return parent1, parent2

    length = len(parent1)

    # Escoge un punto de inicio y final aleatorio para el cruce en el centro
    start, end = sorted(random.sample(range(1, length - 1), 2))

    # Inicializa los hijos con los extremos fijos
    child1 = [parent1[0]] + [-1] * (length - 2) + [parent1[-1]]
    child2 = [parent2[0]] + [-1] * (length - 2) + [parent2[-1]]

    # Llena el centro de los hijos con elementos de los padres
    child1[start:end + 1] = parent2[start:end + 1]
    child2[start:end + 1] = parent1[start:end + 1]

    # Completa los hijos con elementos de los padres, evitando duplicados
    remaining1 = [node for node in parent1 if node not in child1]
    remaining2 = [node for node in parent2 if node not in child2]

    for i in range(1, length - 1):
        if child1[i] == -1:
            if remaining1:
                child1[i] = remaining1.pop(0)
        if child2[i] == -1:
            if remaining2:
                child2[i] = remaining2.pop(0)

    return child1, child2


# Función de mutación - Swap Mutation para nodos intermedios (excluyendo extremos fijos)
def mutate(individual):
    # Obtiene todos los índices de los nodos que son intermedios (sin incluir extremos fijos)
    intermediate_indices = [i for i in range(1, len(individual) - 1)]

    if len(intermediate_indices) < 2:
        # No hay suficientes nodos intermedios para intercambiar, no se hace nada
        return

    # Selecciona dos índices diferentes al azar de los nodos intermedios
    index1, index2 = random.sample(intermediate_indices, 2)

    # Intercambia los nodos en los índices seleccionados
    individual[index1], individual[index2] = individual[index2], individual[index1]



# Función principal para ejecutar el algoritmo genético una vez
def genetic_algorithm(start_node, end_node, intermediate_nodes):
    population = generate_population(population_size, min_tour_size, max_tour_size, start_node, end_node,
                                     intermediate_nodes)
    convergence_generation = None  # Variable para almacenar la generación de convergencia
    best_fitness_history = []  # Historial de los mejores valores de aptitud en cada generación

    for generation in range(generations):
        new_population = []
        for _ in range(population_size // 2):
            parents = select(population, 2)

            # Verifica si los padres tienen la misma longitud antes de realizar el cruzamiento
            if len(parents[0]) == len(parents[1]):
                child1, child2 = crossover(parents[0], parents[1])

                # Verifica si los hijos cumplen con las restricciones antes de agregarlos
                if evaluate_restrictions(child1):
                    new_population.append(child1)
                if evaluate_restrictions(child2):
                    new_population.append(child2)
            else:
                # Si los padres tienen diferentes longitudes, simplemente añade los padres a la nueva población
                new_population.extend(parents)

        for individual in new_population:
            if random.random() < mutation_prob:
                mutate(individual)

        population = new_population

        # Calcular el mejor individuo en esta generación
        best_individual = min(population, key=lambda x: evaluate_individual(x, distance_matrix))
        best_fitness = evaluate_individual(best_individual, distance_matrix)
        best_fitness_history.append(best_fitness)

        # Imprimir información sobre esta generación
        print("Generación {}: Mejor distancia: {}".format(generation + 1, best_fitness))

        # Verificar convergencia (si la distancia no mejora significativamente)
        if generation > 0:
            prev_best_fitness = best_fitness_history[-2]
            if best_fitness == prev_best_fitness:
                convergence_generation = generation
                print("Convergencia detectada en la generación {}.".format(convergence_generation + 1))
                break  # Puedes detener el algoritmo aquí si lo deseas

    if convergence_generation is None:
        print("No se detectó convergencia después de {} generaciones.".format(generations))

    return best_individual, best_fitness



if __name__ == "__main__":
    best_solutions = []  # Almacenar las mejores soluciones de cada ejecución
    best_distances = []  # Almacenar las distancias de las mejores soluciones

    for _ in range(num_runs):
        print("\nEjecución {}:".format(_ + 1))
        best_solution, best_distance = genetic_algorithm(start_node, end_node, intermediate_nodes)
        best_solutions.append(best_solution)
        best_distances.append(best_distance)

    # Encuentra el índice de la mejor solución
    best_index = np.argmin(best_distances)

    print("\nMejor recorrido encontrado en la ejecución {}:".format(best_index + 1))
    print("Recorrido:", best_solutions[best_index])
    print("Distancia total:", best_distances[best_index])

    # Calcula estadísticas sobre las soluciones encontradas
    avg_distance = np.mean(best_distances)
    std_distance = np.std(best_distances)
    print("\nEstadísticas sobre las ejecuciones:")
    print("Distancia promedio:", avg_distance)
    print("Desviación estándar de la distancia:", std_distance)
