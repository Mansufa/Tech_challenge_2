import pytest
import random
import math
from genetic_algorithm import (
    calculate_distance,
    calculate_fitness,
    order_crossover,
    mutate,
    sort_population,
    generate_random_population
)

# Dados de exemplo para os testes
@pytest.fixture
def cities():
    """Fixture com uma lista de cidades para os testes."""
    return [(0, 0), (30, 0), (30, 40), (0, 40)]

@pytest.fixture
def depot():
    """Fixture para a localização do depósito."""
    return (0, 0)


def test_calculate_distance():
    """Testa o cálculo da distância euclidiana."""
    assert calculate_distance((0, 0), (3, 4)) == 5.0
    assert calculate_distance((10, 20), (10, 20)) == 0.0


def test_generate_random_population(cities):
    """Testa se a população inicial é gerada corretamente."""
    population_size = 10
    population = generate_random_population(cities, population_size)

    assert len(population) == population_size
    # Verifica se cada indivíduo é uma permutação válida das cidades
    for individual in population:
        assert len(individual) == len(cities)
        assert sorted(individual) == sorted(cities)


def test_calculate_fitness_simple_tsp(cities, depot):
    """Testa o fitness para um TSP simples (1 veículo, sem restrições)."""
    # Rota: (0,0) -> (30,0) -> (30,40) -> (0,40)
    # Distância: 30 + 40 + 30 = 100
    # A função de fitness atual adiciona a volta ao depósito
    # Distância com retorno ao depósito: 100 + 40 = 140
    path = [cities[0], cities[1], cities[2], cities[3]]
    # A função de fitness usa o depot (0,0) por padrão, que é a primeira cidade
    expected_distance = 30 + 40 + 30 + 40
    fitness, routes = calculate_fitness(path, depot=depot, return_routes=True)

    assert fitness == pytest.approx(expected_distance)
    assert len(routes) == 1
    assert len(routes[0]) == 4 # 4 cidades na única rota


def test_calculate_fitness_multi_vehicle(cities, depot):
    """Testa o fitness com múltiplos veículos."""
    path = [cities[1], cities[2], cities[3]] # (30,0), (30,40), (0,40)
    # Veículo 1: (0,0)->(30,0)->(0,0) = 30+30=60
    # Veículo 2: (0,0)->(30,40)->(0,0) = 50+50=100
    # Veículo 3: (0,0)->(0,40)->(0,0) = 40+40=80
    # Total = 240
    fitness, routes = calculate_fitness(path, vehicle_count=3, depot=depot, return_routes=True)

    assert fitness == pytest.approx(240)
    assert len(routes) == 3
    assert len(routes[0]) == 1 and routes[0][0] == 0 # city_idx 0 do path
    assert len(routes[1]) == 1 and routes[1][0] == 1 # city_idx 1 do path
    assert len(routes[2]) == 1 and routes[2][0] == 2 # city_idx 2 do path


def test_calculate_fitness_capacity_penalty(cities, depot):
    """Testa a penalidade por violação de capacidade."""
    path = [cities[1], cities[2]] # (30,0), (30,40)
    demands = [15, 15]
    capacity = 10 # Capacidade do veículo

    # A lógica tentará alocar as duas cidades no mesmo veículo, violando a capacidade
    fitness, routes = calculate_fitness(path, demands=demands, capacity=capacity, depot=depot, return_routes=True)

    # O fitness deve ser alto devido à penalidade
    assert fitness > 10000


def test_calculate_fitness_distance_penalty(cities, depot):
    """Testa a penalidade por violação de distância máxima."""
    path = [cities[1], cities[2]] # (30,0), (30,40)
    max_distance = 50 # Distância máxima por rota

    # Rota: (0,0)->(30,0)->(30,40)->(0,0) = 30 + 40 + 50 = 120, que é > 50
    fitness, routes = calculate_fitness(path, max_distance=max_distance, depot=depot, return_routes=True)

    # O fitness deve ser alto devido à penalidade
    assert fitness > 10000


def test_order_crossover():
    """Testa o operador de crossover (Order Crossover)."""
    parent1 = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    parent2 = [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]

    # Força o corte para ser determinístico no teste
    random.seed(42)
    child = order_crossover(parent1, parent2)

    # Verifica se o filho é uma permutação válida
    assert len(child) == len(parent1)
    assert sorted(child) == sorted(parent1)
    # Verifica se o filho não é igual a nenhum dos pais (na maioria dos casos)
    assert child != parent1
    assert child != parent2


def test_mutate():
    """Testa o operador de mutação."""
    solution = [(1, 1), (2, 2), (3, 3), (4, 4)]

    # Teste com probabilidade 0 (não deve mutar)
    mutated = mutate(solution, mutation_probability=0.0)
    assert mutated == solution

    # Teste com probabilidade 1 (deve mutar)
    random.seed(42) # Garante que o mesmo índice seja escolhido
    mutated = mutate(solution, mutation_probability=1.0)
    assert mutated != solution
    # A mutação atual troca dois elementos adjacentes
    assert mutated == [(1, 1), (3, 3), (2, 2), (4, 4)]


def test_sort_population():
    """Testa a ordenação da população pelo fitness."""
    pop = [[(1,1)], [(2,2)], [(3,3)]]
    fit = [10.0, 5.0, 15.0]

    sorted_pop, sorted_fit = sort_population(pop, fit)

    assert sorted_fit == [5.0, 10.0, 15.0]
    assert sorted_pop[0] == [(2,2)]
    assert sorted_pop[1] == [(1,1)]
    assert sorted_pop[2] == [(3,3)]
