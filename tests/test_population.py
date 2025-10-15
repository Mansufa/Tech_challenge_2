"""Testes unitários para o módulo population.py"""

import sys
from pathlib import Path

import pytest

# Adiciona o diretório src ao path para permitir imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Delivery, Priority
from population import (
    calculate_distance,
    calculate_fitness_multi_vehicle,
    calculate_route_distance,
    create_initial_population_deliveries,
    optimize_vehicle_route_nearest_neighbor,
    split_deliveries_by_vehicle,
)


class TestCreateInitialPopulationDeliveries:
    """Testes para a função create_initial_population_deliveries"""

    def test_create_initial_population_deliveries_success(self):
        # Arrange
        deliveries = [
            Delivery(location=(10, 20), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(30, 40), priority=Priority.MEDIUM, weight=15.0, id=1),
            Delivery(location=(50, 60), priority=Priority.LOW, weight=20.0, id=2),
        ]
        population_size = 10

        # Act
        population = create_initial_population_deliveries(deliveries, population_size)

        # Assert
        assert len(population) == population_size
        assert all(len(individual) == len(deliveries) for individual in population)
        assert all(isinstance(individual, list) for individual in population)
        assert all(all(delivery in individual for delivery in deliveries) for individual in population)


class TestCalculateDistance:
    """Testes para a função calculate_distance"""

    def test_calculate_distance_success(self):
        # Arrange
        city1 = (0.0, 0.0)
        city2 = (3.0, 4.0)

        # Act
        distance = calculate_distance(city1, city2)

        # Assert
        assert distance == pytest.approx(5.0, rel=1e-9)


class TestOptimizeVehicleRouteNearestNeighbor:
    """Testes para a função optimize_vehicle_route_nearest_neighbor"""

    def test_optimize_vehicle_route_nearest_neighbor_success(self):
        # Arrange
        depot = (0, 0)
        route = [
            Delivery(location=(100, 100), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(10, 10), priority=Priority.MEDIUM, weight=15.0, id=1),
            Delivery(location=(50, 50), priority=Priority.LOW, weight=20.0, id=2),
        ]

        # Act
        optimized_route = optimize_vehicle_route_nearest_neighbor(route, depot)

        # Assert
        assert len(optimized_route) == len(route)
        assert all(delivery in optimized_route for delivery in route)
        assert optimized_route[0].location == (10, 10)  # Mais próximo do depósito


class TestSplitDeliveriesByVehicle:
    """Testes para a função split_deliveries_by_vehicle"""

    def test_split_deliveries_by_vehicle_success(self):
        # Arrange
        depot = (0, 0)
        deliveries = [
            Delivery(location=(10, 20), priority=Priority.CRITICAL, weight=10.0, id=0),
            Delivery(location=(30, 40), priority=Priority.HIGH, weight=15.0, id=1),
            Delivery(location=(50, 60), priority=Priority.MEDIUM, weight=20.0, id=2),
            Delivery(location=(70, 80), priority=Priority.LOW, weight=12.0, id=3),
        ]
        num_vehicles = 2
        vehicle_capacities = [30.0, 35.0]
        vehicle_max_deliveries = [2, 2]

        # Act
        vehicle_routes = split_deliveries_by_vehicle(
            deliveries, num_vehicles, depot, vehicle_capacities, vehicle_max_deliveries
        )

        # Assert
        assert len(vehicle_routes) == num_vehicles
        assert all(isinstance(route, list) for route in vehicle_routes)
        all_deliveries = [delivery for route in vehicle_routes for delivery in route]
        assert len(all_deliveries) == len(deliveries)
        assert all(delivery in all_deliveries for delivery in deliveries)


class TestCalculateRouteDistance:
    """Testes para a função calculate_route_distance"""

    def test_calculate_route_distance_success(self):
        # Arrange
        depot = (0, 0)
        route = [
            Delivery(location=(3, 0), priority=Priority.HIGH, weight=10.0, id=0),
            Delivery(location=(3, 4), priority=Priority.MEDIUM, weight=15.0, id=1),
        ]

        # Act
        distance = calculate_route_distance(route, depot)

        # Assert
        expected_distance = 3.0 + 4.0 + 5.0
        assert distance == pytest.approx(expected_distance, rel=1e-9)


class TestCalculateFitnessMultiVehicle:
    """Testes para a função calculate_fitness_multi_vehicle"""

    def test_calculate_fitness_multi_vehicle_success(self):
        # Arrange
        depot = (0, 0)
        deliveries = [
            Delivery(location=(10, 10), priority=Priority.CRITICAL, weight=10.0, id=0),
            Delivery(location=(20, 20), priority=Priority.HIGH, weight=15.0, id=1),
            Delivery(location=(30, 30), priority=Priority.MEDIUM, weight=12.0, id=2),
        ]
        num_vehicles = 2
        vehicle_capacities = [25.0, 25.0]
        vehicle_max_deliveries = [2, 2]

        # Act
        fitness = calculate_fitness_multi_vehicle(
            deliveries, num_vehicles, depot, vehicle_capacities, vehicle_max_deliveries
        )

        # Assert
        assert isinstance(fitness, float)
        assert fitness > 0
        assert fitness != float("inf")
