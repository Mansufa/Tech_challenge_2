

import random
import math
import copy
from typing import List, Tuple

default_problems = {
    5: [(733, 251), (706, 87), (546, 97), (562, 49), (576, 253)],
    10: [(470, 169), (602, 202), (754, 239), (476, 233), (468, 301), (522, 29), (597, 171), (487, 325), (746, 232), (558, 136)],
    12: [(728, 67), (560, 160), (602, 312), (712, 148), (535, 340), (720, 354), (568, 300), (629, 260), (539, 46), (634, 343), (491, 135), (768, 161)],
    15: [(512, 317), (741, 72), (552, 50), (772, 346), (637, 12), (589, 131), (732, 165), (605, 15), (730, 38), (576, 216), (589, 381), (711, 387), (563, 228), (494, 22), (787, 288)]
}


def generate_random_population(cities_location: List[Tuple[float, float]], population_size: int) -> List[List[Tuple[float, float]]]:
    """
    Generate a random population of routes for a given set of cities.

    Parameters:
    - cities_location (List[Tuple[float, float]]): A list of tuples representing the locations of cities,
      where each tuple contains the latitude and longitude.
    - population_size (int): The size of the population, i.e., the number of routes to generate.

    Returns:
    List[List[Tuple[float, float]]]: A list of routes, where each route is represented as a list of city locations.
    """
    return [random.sample(cities_location, len(cities_location)) for _ in range(population_size)]


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate the Euclidean distance between two points.

    Parameters:
    - point1 (Tuple[float, float]): The coordinates of the first point.
    - point2 (Tuple[float, float]): The coordinates of the second point.

    Returns:
    float: The Euclidean distance between the two points.
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_fitness(
    path: List[Tuple[float, float]],
    priorities: List[float] = None,
    demands: List[float] = None,
    vehicle_count: int = 1,
    capacity: float = float("inf"),
    max_distance: float = float("inf"),
    depot: Tuple[float, float] = (0.0, 0.0),
    return_routes: bool = False,
) -> float:
    """
    Calculate a fitness for a route permutation that supports a simple capacitated
    multi-vehicle routing formulation with priorities and maximum route distance.

    Behaviour & assumptions (reasonable defaults applied when arguments omitted):
    - `path` is a permutation (list) of city coordinates (x, y).
    - `priorities` is a list of same length as `path` with higher numbers meaning
      more important customers. If None, all priorities are treated as 1.0.
    - `demands` is a list of same length as `path` describing demand/load per city.
      If None, all demands are treated as 1.0.
    - `vehicle_count` number of vehicles available to serve cities in the order
      they appear in `path`. A simple greedy assignment fills vehicles in sequence.
    - `capacity` per-vehicle capacity. If a single city's demand > capacity the
      city will be assigned but a large penalty is applied.
    - `max_distance` is the maximum allowed route distance per vehicle. If exceeded
      a penalty is applied. Distances include travel from and back to `depot`.
    - `depot` is the vehicle depot coordinates (default (0,0)).
    - By default the function returns a single float (lower is better). If
      `return_routes=True` the function returns a tuple (fitness, routes) where
      `routes` is a list of lists of city indices assigned to each vehicle.

    The fitness is computed as: total_distance + big_penalty * (priority-weighted
    sum of unassigned or severely violated demands) . The design keeps the
    function backward-compatible with existing code that expects a float.
    """
    n = len(path)

    # Default priorities and demands
    if priorities is None:
        priorities = [1.0] * n
    if demands is None:
        demands = [1.0] * n

    # Sanity: if provided lists don't match length, fallback to defaults
    if len(priorities) != n:
        priorities = [1.0] * n
    if len(demands) != n:
        demands = [1.0] * n

    # Prepare assignment structures
    routes: List[List[int]] = [[] for _ in range(vehicle_count)]
    route_loads: List[float] = [0.0] * vehicle_count
    route_distances: List[float] = [0.0] * vehicle_count

    unassigned_indices: List[int] = []

    # Helper to compute route distance given a sequence of points (includes depot returns)
    def route_distance_from_indices(indices: List[int]) -> float:
        if not indices:
            return 0.0
        dist = 0.0
        last = depot
        for idx in indices:
            dist += calculate_distance(last, path[idx])
            last = path[idx]
        dist += calculate_distance(last, depot)
        return dist

    # Greedy assignment: iterate cities in `path` order and try to place into a vehicle
    for city_idx, city in enumerate(path):
        demand = demands[city_idx]
        placed = False
        # Try to place into any vehicle (greedy: fill vehicle 0..V-1)
        for v in range(vehicle_count):
            tentative_indices = routes[v] + [city_idx]
            tentative_load = route_loads[v] + demand
            tentative_distance = route_distance_from_indices(tentative_indices)

            # If tentative respects both capacity and max_distance, accept
            if tentative_load <= capacity and tentative_distance <= max_distance:
                routes[v].append(city_idx)
                route_loads[v] = tentative_load
                route_distances[v] = tentative_distance
                placed = True
                break

        # If couldn't place respecting constraints, try to place anyway in the least-bad vehicle
        if not placed:
            # Find vehicle that increases distance the least (even if it violates constraints)
            best_v = None
            best_extra = float("inf")
            for v in range(vehicle_count):
                tentative_indices = routes[v] + [city_idx]
                tentative_distance = route_distance_from_indices(
                    tentative_indices)
                extra = tentative_distance - route_distances[v]
                if extra < best_extra:
                    best_extra = extra
                    best_v = v

            if best_v is not None:
                routes[best_v].append(city_idx)
                route_loads[best_v] += demand
                route_distances[best_v] = route_distance_from_indices(
                    routes[best_v])
            else:
                unassigned_indices.append(city_idx)

    total_distance = sum(route_distances)

    # Penalties
    PENALTY_UNASSIGNED = 1e6
    PENALTY_CAPACITY = 1e4
    PENALTY_DISTANCE = 1e4

    penalty = 0.0

    # Unassigned cities (ideally shouldn't happen with the greedy fallback, but safe)
    if unassigned_indices:
        penalty += PENALTY_UNASSIGNED * \
            sum(priorities[i] for i in unassigned_indices)

    # Per-route violations
    for v in range(vehicle_count):
        # capacity violation
        if route_loads[v] > capacity:
            # severity scaled by overload and by average priority of route
            avg_priority = (
                sum(priorities[i] for i in routes[v]) /
                len(routes[v]) if routes[v] else 1.0
            )
            overload = route_loads[v] - capacity
            penalty += PENALTY_CAPACITY * overload * avg_priority

        # distance violation
        if route_distances[v] > max_distance:
            avg_priority = (
                sum(priorities[i] for i in routes[v]) /
                len(routes[v]) if routes[v] else 1.0
            )
            excess = route_distances[v] - max_distance
            penalty += PENALTY_DISTANCE * excess * avg_priority

    # Reward serving high-priority customers by subtracting a small fraction of fulfilled priority
    served_priority = 0.0
    for v in range(vehicle_count):
        served_priority += sum(priorities[i] for i in routes[v])

    # Objective: minimize total_distance minus a small reward for serving priority,
    # plus penalties for violations.
    PRIORITY_REWARD = 0.01  # small reward to prefer routes that serve higher priority early
    fitness = total_distance - PRIORITY_REWARD * served_priority + penalty

    if return_routes:
        return fitness, routes

    return fitness


def order_crossover(parent1: List[Tuple[float, float]], parent2: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Perform order crossover (OX) between two parent sequences to create a child sequence.

    Parameters:
    - parent1 (List[Tuple[float, float]]): The first parent sequence.
    - parent2 (List[Tuple[float, float]]): The second parent sequence.

    Returns:
    List[Tuple[float, float]]: The child sequence resulting from the order crossover.
    """
    length = len(parent1)

    # Choose two random indices for the crossover (ensure start < end)
    start_index = random.randint(0, length - 2)
    end_index = random.randint(start_index + 1, length)

    # Prepare an empty child filled with None
    child: List[Tuple[float, float] | None] = [None] * length

    # Copy the segment from parent1 and invert only that segment
    segment = parent1[start_index:end_index]
    inverted_segment = list(reversed(segment))
    child[start_index:end_index] = inverted_segment

    # Fill the remaining positions with genes from parent2 in order
    remaining_genes = [
        gene for gene in parent2 if gene not in inverted_segment]
    rem_idx = 0
    for i in range(length):
        if child[i] is None:
            if rem_idx < len(remaining_genes):
                child[i] = remaining_genes[rem_idx]
                rem_idx += 1
            else:
                # Should not happen, but safety: fill with a random remaining gene
                for gene in parent1:
                    if gene not in child:
                        child[i] = gene
                        break

    # Type ignore: child contains no Nones at this point
    return [c for c in child]  # type: ignore

# demonstration: crossover test code
# Example usage:
# parent1 = [(1, 1), (2, 2), (3, 3), (4,4), (5,5), (6, 6)]
# parent2 = [(6, 6), (5, 5), (4, 4), (3, 3),  (2, 2), (1, 1)]

# # parent1 = [1, 2, 3, 4, 5, 6]
# # parent2 = [6, 5, 4, 3, 2, 1]


# child = order_crossover(parent1, parent2)
# print("Parent 1:", [0, 1, 2, 3, 4, 5, 6, 7, 8])
# print("Parent 1:", parent1)
# print("Parent 2:", parent2)
# print("Child   :", child)


# # Example usage:
# population = generate_random_population(5, 10)

# print(calculate_fitness(population[0]))


# population = [(random.randint(0, 100), random.randint(0, 100))
#           for _ in range(3)]


# TODO: implement a mutation_intensity and invert pieces of code instead of just swamping two.
def mutate(solution:  List[Tuple[float, float]], mutation_probability: float) -> List[Tuple[float, float]]:
    """
    Mutate a solution by inverting a segment of the sequence with a given mutation probability.

    Parameters:
    - solution (List[int]): The solution sequence to be mutated.
    - mutation_probability (float): The probability of mutation for each individual in the solution.

    Returns:
    List[int]: The mutated solution sequence.
    """
    mutated_solution = copy.deepcopy(solution)

    # Check if mutation should occur
    if random.random() < mutation_probability:

        # Ensure there are at least two cities to perform a swap
        if len(solution) < 2:
            return solution

        # Select a random index (excluding the last index) for swapping
        index = random.randint(0, len(solution) - 2)

        # Swap the cities at the selected index and the next index
        mutated_solution[index], mutated_solution[index +
                                                  1] = solution[index + 1], solution[index]

    return mutated_solution

# Demonstration: mutation test code
# # Example usage:
# original_solution = [(1, 1), (2, 2), (3, 3), (4, 4)]
# mutation_probability = 1

# mutated_solution = mutate(original_solution, mutation_probability)
# print("Original Solution:", original_solution)
# print("Mutated Solution:", mutated_solution)


def sort_population(population: List[List[Tuple[float, float]]], fitness: List[float]) -> Tuple[List[List[Tuple[float, float]]], List[float]]:
    """
    Sort a population based on fitness values.

    Parameters:
    - population (List[List[Tuple[float, float]]]): The population of solutions, where each solution is represented as a list.
    - fitness (List[float]): The corresponding fitness values for each solution in the population.

    Returns:
    Tuple[List[List[Tuple[float, float]]], List[float]]: A tuple containing the sorted population and corresponding sorted fitness values.
    """
    # Combine lists into pairs
    combined_lists = list(zip(population, fitness))

    # Sort based on the values of the fitness list
    sorted_combined_lists = sorted(combined_lists, key=lambda x: x[1])

    # Separate the sorted pairs back into individual lists
    sorted_population, sorted_fitness = zip(*sorted_combined_lists)

    return sorted_population, sorted_fitness


if __name__ == '__main__':
    N_CITIES = 10

    POPULATION_SIZE = 100
    N_GENERATIONS = 100
    MUTATION_PROBABILITY = 0.3
    cities_locations = [(random.randint(0, 100), random.randint(0, 100))
                        for _ in range(N_CITIES)]

    # CREATE INITIAL POPULATION
    population = generate_random_population(cities_locations, POPULATION_SIZE)

    # Lists to store best fitness and generation for plotting
    best_fitness_values = []
    best_solutions = []

    for generation in range(N_GENERATIONS):

        population_fitness = [calculate_fitness(
            individual) for individual in population]

        population, population_fitness = sort_population(
            population,  population_fitness)

        best_fitness = calculate_fitness(population[0])
        best_solution = population[0]

        best_fitness_values.append(best_fitness)
        best_solutions.append(best_solution)

        print(f"Generation {generation}: Best fitness = {best_fitness}")

        new_population = [population[0]]  # Keep the best individual: ELITISM

        while len(new_population) < POPULATION_SIZE:

            # SELECTION
            # Select parents from the top 10 individuals
            parent1, parent2 = random.choices(population[:10], k=2)

            # CROSSOVER
            child1 = order_crossover(parent1, parent2)

            # MUTATION
            child1 = mutate(child1, MUTATION_PROBABILITY)

            new_population.append(child1)

        print('generation: ', generation)
        population = new_population
