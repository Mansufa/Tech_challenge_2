import sys
from pathlib import Path

import pytest

# Adiciona o diretório src ao path para permitir imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cities import (
    generate_cities,
    generate_deliveries,
    generate_vehicle_capacities,
    generate_vehicle_max_deliveries,
)
from models import Delivery, Priority


class TestGenerateCities:
    """Testes para a função generate_cities"""

    def test_generate_cities_success(self):
        # Arrange
        num_cities = 10
        min_distance = 30
        max_attempts = 1000

        # Act
        cities = generate_cities(num_cities, min_distance, max_attempts)

        # Assert
        assert len(cities) == num_cities
        assert all(isinstance(city, tuple) for city in cities)
        assert all(len(city) == 2 for city in cities)
        assert all(isinstance(coord, int) for city in cities for coord in city)


class TestGenerateDeliveries:
    """Testes para a função generate_deliveries"""

    def test_generate_deliveries_success(self):
        # Arrange
        num_deliveries = 15
        min_distance = 30
        max_attempts = 1000

        # Act
        deliveries = generate_deliveries(num_deliveries, min_distance, max_attempts)

        # Assert
        assert len(deliveries) == num_deliveries
        assert all(isinstance(delivery, Delivery) for delivery in deliveries)
        assert all(isinstance(delivery.priority, Priority) for delivery in deliveries)
        assert all(delivery.weight > 0 for delivery in deliveries)
        assert all(isinstance(delivery.location, tuple) for delivery in deliveries)
        assert all(len(delivery.location) == 2 for delivery in deliveries)


class TestGenerateVehicleCapacities:
    """Testes para a função generate_vehicle_capacities"""

    def test_generate_vehicle_capacities_success(self):
        # Arrange
        total_weight = 100.0
        num_vehicles = 3
        margin = 1.1

        # Act
        capacities = generate_vehicle_capacities(total_weight, num_vehicles, margin)

        # Assert
        assert len(capacities) == num_vehicles
        assert all(isinstance(capacity, float) for capacity in capacities)
        assert all(capacity > 0 for capacity in capacities)
        assert sum(capacities) == pytest.approx(total_weight * margin, rel=0.1)


class TestGenerateVehicleMaxDeliveries:
    """Testes para a função generate_vehicle_max_deliveries"""

    def test_generate_vehicle_max_deliveries_success(self):
        # Arrange
        num_deliveries = 15
        num_vehicles = 3

        # Act
        max_deliveries = generate_vehicle_max_deliveries(num_deliveries, num_vehicles)

        # Assert
        assert len(max_deliveries) == num_vehicles
        assert all(isinstance(count, int) for count in max_deliveries)
        assert all(count >= 1 for count in max_deliveries)
        assert sum(max_deliveries) == num_deliveries
