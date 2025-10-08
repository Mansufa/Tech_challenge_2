import random
from typing import List, Tuple


def create_initial_population(cities: List[Tuple[int, int]], population_size: int) -> List[List[Tuple[int, int]]]:
    return [random.sample(cities, len(cities)) for _ in range(population_size)]


def calculate_fitness_simple(path: List[Tuple[float, float]]) -> float:
    total_distance = 0.0

    # Distância entre cidades consecutivas
    for i in range(len(path) - 1):
        total_distance += calculate_distance(path[i], path[i + 1])

    # Distância de volta ao início (circuito fechado)
    total_distance += calculate_distance(path[-1], path[0])

    return total_distance


def calculate_distance(city1: Tuple[float, float], city2: Tuple[float, float]) -> float:
    """Calcula distância euclidiana entre duas cidades."""
    return ((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2) ** 0.5


