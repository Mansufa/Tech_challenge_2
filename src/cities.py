import random
from typing import List, Tuple

from config import (
    HEIGHT,
    MARGIN,
    MAX_DELIVERY_WEIGHT,
    MIN_DELIVERY_WEIGHT,
    PLOT_X_OFFSET,
    WIDTH,
)
from models import Delivery, Priority
from population import calculate_distance


def generate_cities(
    num_cities: int,
    min_distance: int = 30,
    max_attempts: int = 1000,
) -> List[Tuple[int, int]]:
    """
    Gera coordenadas aleatórias para cidades respeitando distância mínima.
    """
    cities = []
    attempts = 0

    while len(cities) < num_cities and attempts < max_attempts:
        attempts += 1

        x = random.randint(PLOT_X_OFFSET + MARGIN, WIDTH - MARGIN)
        y = random.randint(MARGIN, HEIGHT - MARGIN)
        candidate = (x, y)

        valid_position = True
        for existing_city in cities:
            if calculate_distance(candidate, existing_city) < min_distance:
                valid_position = False
                break

        if valid_position:
            cities.append(candidate)
            attempts = 0

    if len(cities) < num_cities:
        while len(cities) < num_cities:
            x = random.randint(PLOT_X_OFFSET + MARGIN, WIDTH - MARGIN)
            y = random.randint(MARGIN, HEIGHT - MARGIN)
            cities.append((x, y))

    return cities


def generate_deliveries(
    num_deliveries: int,
    min_distance: int = 30,
    max_attempts: int = 1000,
) -> List[Delivery]:
    """
    Gera entregas com localizações, prioridades e pesos aleatórios.
    """
    locations = generate_cities(num_deliveries, min_distance, max_attempts)

    # Define distribuição de prioridades (proporções)
    priority_distribution = [
        (Priority.CRITICAL, 0.10),  # 10% críticas
        (Priority.HIGH, 0.20),  # 20% altas
        (Priority.MEDIUM, 0.40),  # 40% médias
        (Priority.LOW, 0.30),  # 30% baixas
    ]

    # Calcula quantas entregas de cada prioridade
    priorities = []
    for priority, proportion in priority_distribution:
        count = int(num_deliveries * proportion)
        priorities.extend([priority] * count)

    while len(priorities) < num_deliveries:
        priorities.append(Priority.MEDIUM)

    # Embaralha para randomizar distribuição espacial
    random.shuffle(priorities)

    # Cria entregas com pesos aleatórios
    deliveries = []
    for i, (location, priority) in enumerate(zip(locations, priorities, strict=False)):
        weight = random.uniform(MIN_DELIVERY_WEIGHT, MAX_DELIVERY_WEIGHT)
        delivery = Delivery(location=location, priority=priority, weight=round(weight, 2), id=i)
        deliveries.append(delivery)

    return deliveries


def generate_vehicle_capacities(total_weight: float, num_vehicles: int, margin: float = 1.1) -> List[float]:
    """
    Gera capacidades aleatórias para veículos.
    """
    total_capacity = total_weight * margin

    random_weights = [random.random() for _ in range(num_vehicles)]
    total_random = sum(random_weights)

    # Distribui a capacidade proporcionalmente
    capacities = []
    for weight in random_weights:
        proportion = weight / total_random
        vehicle_capacity = total_capacity * proportion
        capacities.append(round(vehicle_capacity, 1))

    return capacities
