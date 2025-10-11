import random
from typing import List, Tuple

from config import (
    PENALTY_EXCEEDS_RANGE,
    PENALTY_OVERLOAD,
    PENALTY_PRIORITY,
    VEHICLE_MAX_DISTANCE,
)
from models import Delivery, Priority


def create_initial_population_deliveries(deliveries: List[Delivery], population_size: int) -> List[List[Delivery]]:
    """Cria população inicial de rotas de entregas aleatórias."""
    return [random.sample(deliveries, len(deliveries)) for _ in range(population_size)]


def calculate_distance(city1: Tuple[float, float], city2: Tuple[float, float]) -> float:
    """Calcula distância euclidiana entre duas cidades."""
    return ((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2) ** 0.5


def optimize_vehicle_route_nearest_neighbor(route: List[Delivery], depot: Tuple[int, int]) -> List[Delivery]:
    """Otimiza a rota de um veículo usando a heurística do vizinho mais próximo."""
    if not route:
        return route

    if len(route) == 1:
        return route

    optimized = []
    current_position = depot
    remaining = route.copy()

    while remaining:
        # Encontra a entrega mais próxima da posição atual
        nearest = min(remaining, key=lambda delivery: calculate_distance(current_position, delivery.location))

        optimized.append(nearest)

        current_position = nearest.location

        remaining.remove(nearest)

    return optimized


def split_deliveries_by_vehicle(deliveries: List[Delivery], num_vehicles: int, depot: Tuple[int, int], vehicle_capacities: List[float]) -> List[List[Delivery]]:
    sorted_deliveries = deliveries.copy()

    sorted_deliveries.sort(key=lambda d: d.priority.value)

    # Inicializa rotas e cargas de cada veículo
    vehicle_routes = [[] for _ in range(num_vehicles)]
    vehicle_loads = [0.0 for _ in range(num_vehicles)]

    for delivery in sorted_deliveries:
        # Encontra veículo com menor carga que ainda tem espaço
        best_vehicle = None
        min_load = float("inf")

        for i in range(num_vehicles):
            if vehicle_loads[i] + delivery.weight <= vehicle_capacities[i]:
                if vehicle_loads[i] < min_load:
                    min_load = vehicle_loads[i]
                    best_vehicle = i

        if best_vehicle is None:
            best_vehicle = vehicle_loads.index(min(vehicle_loads))

        vehicle_routes[best_vehicle].append(delivery)
        vehicle_loads[best_vehicle] += delivery.weight

    optimized_routes = []
    for route in vehicle_routes:
        optimized_route = optimize_vehicle_route_nearest_neighbor(route, depot)
        optimized_routes.append(optimized_route)

    return optimized_routes


def calculate_route_distance(route: List[Delivery], depot: Tuple[int, int]) -> float:
    total = 0.0

    total += calculate_distance(depot, route[0].location)

    for i in range(len(route) - 1):
        total += calculate_distance(route[i].location, route[i + 1].location)

    total += calculate_distance(route[-1].location, depot)

    return total


def calculate_fitness_multi_vehicle(deliveries: List[Delivery], num_vehicles: int, depot: Tuple[int, int], vehicle_capacities: List[float]) -> float:
    if not deliveries:
        return float("inf")

    vehicle_routes = split_deliveries_by_vehicle(deliveries, num_vehicles, depot, vehicle_capacities)

    total_distance = 0.0
    priority_penalty = 0.0
    capacity_penalty = 0.0
    range_penalty = 0.0

    for vehicle_id, route in enumerate(vehicle_routes):
        if not route:
            continue

        route_distance = calculate_route_distance(route, depot)
        total_distance += route_distance

        # Penaliza prioridades mal posicionadas
        for delivery in route:
            global_position = deliveries.index(delivery)
            total_deliveries = len(deliveries)

            if delivery.priority == Priority.CRITICAL and global_position > total_deliveries * 0.2:
                priority_penalty += PENALTY_PRIORITY * 3.0
            elif delivery.priority == Priority.HIGH and global_position > total_deliveries * 0.4:
                priority_penalty += PENALTY_PRIORITY * 2.0
            elif delivery.priority == Priority.MEDIUM and global_position > total_deliveries * 0.8:
                priority_penalty += PENALTY_PRIORITY * 1.0

        route_load = sum(d.weight for d in route)
        vehicle_capacity = vehicle_capacities[vehicle_id]

        if route_load > vehicle_capacity:
            overload = route_load - vehicle_capacity
            capacity_penalty += PENALTY_OVERLOAD * (overload / vehicle_capacity)

        # Penaliza excesso de autonomia
        if route_distance > VEHICLE_MAX_DISTANCE:
            excess_distance = route_distance - VEHICLE_MAX_DISTANCE
            range_penalty += PENALTY_EXCEEDS_RANGE * (excess_distance / VEHICLE_MAX_DISTANCE)

    if priority_penalty > 0 or capacity_penalty > 0 or range_penalty > 0:
        return total_distance + priority_penalty + capacity_penalty + range_penalty

    return total_distance
