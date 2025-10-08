import copy
import random
from typing import List, Tuple


def order_crossover(parent1: List[Tuple[int, int]], parent2: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    length = len(parent1)

    # Escolhe dois índices aleatórios
    start_index = random.randint(0, length - 1)
    end_index = random.randint(start_index + 1, length)

    # Inicializa o filho com a subsequência do parent1
    child = parent1[start_index:end_index]

    # Preenche as posições restantes com genes do parent2
    remaining_positions = [i for i in range(length) if i < start_index or i >= end_index]
    remaining_genes = [gene for gene in parent2 if gene not in child]

    for position, gene in zip(remaining_positions, remaining_genes):
        child.insert(position, gene)

    return child


def swap_mutation(individual: List[Tuple[float, float]], mutation_probability: float) -> List[Tuple[float, float]]:
    mutated = copy.deepcopy(individual)

    if random.random() < mutation_probability:
        # Seleciona um índice aleatório (excluindo o último)
        index = random.randint(0, len(individual) - 2)

        mutated[index] = individual[index + 1]
        mutated[index + 1] = individual[index]

    return mutated
