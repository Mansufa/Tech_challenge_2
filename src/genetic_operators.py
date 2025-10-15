import copy
import random
from typing import List, Tuple, TypeVar

from models import Delivery

T = TypeVar("T", Tuple[int, int], Delivery)


def sort_population(population: List[List[T]], fitness_scores: List[float]) -> Tuple[List[List[T]], List[float]]:
    sorted_pairs = sorted(zip(fitness_scores, population, strict=False), key=lambda x: x[0])
    sorted_fitness = [fit for fit, _ in sorted_pairs]
    sorted_population = [ind for _, ind in sorted_pairs]
    return sorted_population, sorted_fitness


def order_crossover(parent1: List[T], parent2: List[T]) -> List[T]:
    length = len(parent1)

    start_index = random.randint(0, length - 1)
    end_index = random.randint(start_index + 1, length)

    child = parent1[start_index:end_index]

    remaining_positions = [i for i in range(length) if i < start_index or i >= end_index]
    remaining_genes = [gene for gene in parent2 if gene not in child]

    for position, gene in zip(remaining_positions, remaining_genes, strict=False):
        child.insert(position, gene)

    return child


def swap_mutation(individual: List[T], mutation_probability: float) -> List[T]:
    mutated = copy.deepcopy(individual)

    if random.random() < mutation_probability:
        index = random.randint(0, len(individual) - 2)

        mutated[index] = individual[index + 1]
        mutated[index + 1] = individual[index]

    return mutated
