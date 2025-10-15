import sys
from pathlib import Path

# Adiciona o diretório src ao path para permitir imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from genetic_operators import (
    order_crossover,
    sort_population,
    swap_mutation,
)
from models import Delivery, Priority


class TestSortPopulation:
    """Testes para a função sort_population"""

    def test_sort_population_success(self):
        # Arrange
        population = [
            [(10, 20), (30, 40), (50, 60)],
            [(15, 25), (35, 45), (55, 65)],
            [(5, 15), (25, 35), (45, 55)],
        ]
        fitness_scores = [100.0, 50.0, 75.0]

        # Act
        sorted_pop, sorted_fitness = sort_population(population, fitness_scores)

        # Assert
        assert len(sorted_pop) == len(population)
        assert len(sorted_fitness) == len(fitness_scores)
        assert sorted_fitness == [50.0, 75.0, 100.0]
        assert sorted_pop[0] == population[1]
        assert sorted_pop[1] == population[2]
        assert sorted_pop[2] == population[0]


class TestOrderCrossover:
    """Testes para a função order_crossover"""

    def test_order_crossover_with_tuples_success(self):
        # Arrange
        parent1 = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
        parent2 = [(3, 4), (7, 8), (1, 2), (9, 10), (5, 6)]

        # Act
        child = order_crossover(parent1, parent2)

        # Assert
        assert len(child) == len(parent1)
        assert set(child) == set(parent1)
        assert all(gene in parent1 for gene in child)

    def test_order_crossover_with_deliveries_success(self):
        # Arrange
        parent1 = [
            Delivery(location=(10, 20), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(30, 40), priority=Priority.MEDIUM, weight=15.0, id=1),
            Delivery(location=(50, 60), priority=Priority.LOW, weight=20.0, id=2),
            Delivery(location=(70, 80), priority=Priority.CRITICAL, weight=12.0, id=3),
        ]
        parent2 = [
            Delivery(location=(30, 40), priority=Priority.MEDIUM, weight=15.0, id=1),
            Delivery(location=(70, 80), priority=Priority.CRITICAL, weight=12.0, id=3),
            Delivery(location=(10, 20), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(50, 60), priority=Priority.LOW, weight=20.0, id=2),
        ]

        # Act
        child = order_crossover(parent1, parent2)

        # Assert
        assert len(child) == len(parent1)
        assert all(delivery in parent1 for delivery in child)
        assert len(child) == len(parent1)


class TestSwapMutation:
    """Testes para a função swap_mutation"""

    def test_swap_mutation_with_tuples_success(self):
        # Arrange
        individual = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
        mutation_probability = 1.0  # Garante que a mutação ocorra

        # Act
        mutated = swap_mutation(individual, mutation_probability)

        # Assert
        assert len(mutated) == len(individual)
        assert set(mutated) == set(individual)
        assert mutated != individual or len(individual) <= 1

    def test_swap_mutation_with_deliveries_success(self):
        # Arrange
        individual = [
            Delivery(location=(10, 20), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(30, 40), priority=Priority.MEDIUM, weight=15.0, id=1),
            Delivery(location=(50, 60), priority=Priority.LOW, weight=20.0, id=2),
            Delivery(location=(70, 80), priority=Priority.CRITICAL, weight=12.0, id=3),
        ]
        mutation_probability = 1.0  # Garante que a mutação ocorra

        # Act
        mutated = swap_mutation(individual, mutation_probability)

        # Assert
        assert len(mutated) == len(individual)
        assert all(delivery in individual for delivery in mutated)
        assert mutated is not individual
