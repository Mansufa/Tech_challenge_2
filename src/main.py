import os
import random

import numpy as np
import pygame

from cities import generate_deliveries, generate_vehicle_capacities
from config import (
    FLEET_CAPACITY_MARGIN,
    FPS,
    HEIGHT,
    MUTATION_PROBABILITY,
    N_CITIES,
    NODE_RADIUS,
    NUM_VEHICLES,
    POPULATION_SIZE,
    VEHICLE_MAX_DISTANCE,
    WHITE,
    WIDTH,
)
from genetic_operators import order_crossover, sort_population, swap_mutation
from models import Priority
from population import (
    calculate_fitness_multi_vehicle,
    calculate_route_distance,
    create_initial_population_deliveries,
    split_deliveries_by_vehicle,
)
from visualization import draw_deliveries, draw_depot, draw_legend, draw_multiple_routes, draw_plot


DEPOT_LOCATION = (500, HEIGHT // 2)

deliveries = generate_deliveries(num_deliveries=N_CITIES)
print(f"Entregas geradas: {len(deliveries)}")

total_weight = sum(d.weight for d in deliveries)

vehicle_capacities = generate_vehicle_capacities(total_weight, NUM_VEHICLES, FLEET_CAPACITY_MARGIN)
total_capacity = sum(vehicle_capacities)

print(f"\nVeículos disponíveis: {NUM_VEHICLES}")
for i, capacity in enumerate(vehicle_capacities, 1):
    print(f"  V{i}: Capacidade = {capacity:.1f}kg")

# Estatísticas das entregas
priority_counts = dict.fromkeys(Priority, 0)
for delivery in deliveries:
    priority_counts[delivery.priority] += 1

print("\nDistribuição de prioridades:")
for priority, count in priority_counts.items():
    print(f"  {priority.name}: {count} entregas")

print(f"\nPeso total dos medicamentos: {total_weight:.2f}kg")
print(f"Capacidade total da frota: {total_capacity:.2f}kg")
print(
    f"Margem de segurança: {total_capacity - total_weight:.2f}kg ({((total_capacity / total_weight - 1) * 100):.1f}%)"
)
print(f"Autonomia por veículo: {VEHICLE_MAX_DISTANCE:.0f} unidades")

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VRP Solver - Algoritmo Genético com Prioridades")
clock = pygame.time.Clock()

# Cria população inicial
population = create_initial_population_deliveries(deliveries, POPULATION_SIZE)
best_fitness_values = []
best_solutions = []
generation = 0

print(f"\nPopulação inicial criada: {POPULATION_SIZE} indivíduos")
print("Iniciando evolução...\n")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    generation += 1

    screen.fill(WHITE)

    population_fitness = [
        calculate_fitness_multi_vehicle(individual, NUM_VEHICLES, DEPOT_LOCATION, vehicle_capacities)
        for individual in population
    ]

    population, population_fitness = sort_population(population, population_fitness)

    best_fitness = population_fitness[0]
    best_solution = population[0]
    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    draw_plot(screen, list(range(1, len(best_fitness_values) + 1)), best_fitness_values)

    best_routes = split_deliveries_by_vehicle(best_solution, NUM_VEHICLES, DEPOT_LOCATION, vehicle_capacities)

    draw_deliveries(screen, deliveries, NODE_RADIUS)

    draw_depot(screen, DEPOT_LOCATION, NODE_RADIUS)

    draw_multiple_routes(screen, best_routes, DEPOT_LOCATION)

    draw_legend(screen)

    stats_lines = []
    for vehicle_id, route in enumerate(best_routes, 1):
        route_load = sum(d.weight for d in route)
        route_distance = calculate_route_distance(route, DEPOT_LOCATION)

        # Capacidade específica deste veículo
        vehicle_capacity = vehicle_capacities[vehicle_id - 1]

        overload = max(0, route_load - vehicle_capacity)
        exceed_range = max(0, route_distance - VEHICLE_MAX_DISTANCE)

        vehicle_stats = (
            f"V{vehicle_id}: {len(route)} entregas, {round(route_load, 1)}kg/{round(vehicle_capacity, 1)}kg, "
            f"{round(route_distance, 0)}dist"
        )
        stats_lines.append(vehicle_stats)

    print(f"Geração {generation}: Fitness = {round(best_fitness, 2)} | " + " | ".join(stats_lines))

    new_population = [population[0]]  # Elitismo

    while len(new_population) < POPULATION_SIZE:
        # Seleção: probabilidade inversamente proporcional ao fitness
        probability = 1 / np.array(population_fitness)
        parent1, parent2 = random.choices(population, weights=probability, k=2)

        # Crossover
        child = order_crossover(parent1, parent2)

        # Mutação
        child = swap_mutation(child, MUTATION_PROBABILITY)

        new_population.append(child)

    population = new_population

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()

best_route = best_solutions[best_fitness_values.index(min(best_fitness_values))]
best_vehicle_routes = split_deliveries_by_vehicle(best_route, NUM_VEHICLES, DEPOT_LOCATION, vehicle_capacities)

print("\n" + "=" * 60)
print("MELHOR SOLUÇÃO ENCONTRADA")
print("=" * 60)
print(f"Fitness: {min(best_fitness_values):.2f}")
print(f"Total de gerações: {generation}")

# Analisa cada veículo
print("\nRotas por veículo:")
for vehicle_id, route in enumerate(best_vehicle_routes, 1):
    route_load = sum(d.weight for d in route)
    route_distance = calculate_route_distance(route, DEPOT_LOCATION)
    vehicle_capacity = vehicle_capacities[vehicle_id - 1]

    print(f"\nVeículo {vehicle_id}:")
    print(f"  Capacidade do veículo: {vehicle_capacity:.2f}kg")
    print(f"  Entregas: {len(route)}")
    print(f"  Carga: {route_load:.2f}kg / {vehicle_capacity:.2f}kg", end="")
    print(f"  Distância: {route_distance:.0f} / {VEHICLE_MAX_DISTANCE:.0f}", end="")

    if route:
        print("  Primeiras entregas:")
        for i, delivery in enumerate(route[:5], 1):
            print(f"    {i}. Prioridade {delivery.priority.name} - {delivery.weight}kg")


print("\n" + "=" * 60)
print("SALVANDO TOP 5 MELHORES SOLUÇÕES")
print("=" * 60)

images_dir = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(images_dir, exist_ok=True)

# Encontra soluções únicas removendo duplicatas
unique_solutions = []
seen_solutions = set()

for fitness, solution in zip(best_fitness_values, best_solutions, strict=False):
    solution_tuple = tuple(d.id for d in solution)  # Usa IDs das entregas
    if solution_tuple not in seen_solutions:
        seen_solutions.add(solution_tuple)
        unique_solutions.append((fitness, solution))

# Ordena por fitness e pega as 5 melhores únicas
unique_solutions.sort(key=lambda x: x[0])
top_5_solutions = unique_solutions[:5]

print(f"Soluções únicas encontradas: {len(unique_solutions)}")
print(f"Salvando as {len(top_5_solutions)} melhores\n")

# Reinicializa pygame para renderizar as imagens
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

for rank, (fitness, solution) in enumerate(top_5_solutions, 1):
    screen.fill(WHITE)

    # Divide entregas entre veículos
    vehicle_routes = split_deliveries_by_vehicle(solution, NUM_VEHICLES, DEPOT_LOCATION, vehicle_capacities)

    # Desenha todos os elementos
    draw_deliveries(screen, deliveries, NODE_RADIUS)
    draw_depot(screen, DEPOT_LOCATION, NODE_RADIUS)
    draw_multiple_routes(screen, vehicle_routes, DEPOT_LOCATION)
    draw_legend(screen)

    # Adiciona texto com informações da solução
    font = pygame.font.Font(None, 28)
    title_text = font.render(f"Top {rank} - Fitness: {fitness:.2f}", True, (0, 0, 0))
    screen.blit(title_text, (10, 10))

    pygame.display.flip()

    filename = f"top_{rank}.png"
    filepath = os.path.join(images_dir, filename)
    pygame.image.save(screen, filepath)

    print(f"✓ Salva: {filename} - Fitness: {fitness:.2f}")

pygame.quit()
