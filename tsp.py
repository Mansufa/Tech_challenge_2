import pygame
from pygame.locals import *
import random
import itertools
from genetic_algorithm import mutate, order_crossover, generate_random_population, calculate_fitness, sort_population, default_problems
from draw_functions import draw_paths, draw_plot, draw_cities
import time
import csv
import json
import sys
import numpy as np
import pygame
from benchmark_att48 import *


# Define constant values
# pygame
WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450

# GA
N_CITIES = 15
POPULATION_SIZE = 100
N_GENERATIONS = None
TIME_LIMIT_SECONDS = 120  # 2 minutes
MUTATION_PROBABILITY = 0.5

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Initialize problem
# Using Random cities generation
# cities_locations = [(random.randint(NODE_RADIUS + PLOT_X_OFFSET, WIDTH - NODE_RADIUS), random.randint(NODE_RADIUS, HEIGHT - NODE_RADIUS))
#                     for _ in range(N_CITIES)]


# # # Using Deault Problems: 10, 12 or 15
# WIDTH, HEIGHT = 800, 400
# cities_locations = default_problems[15]


# Using att48 benchmark
WIDTH, HEIGHT = 1500, 800
att_cities_locations = np.array(att_48_cities_locations)
max_x = max(point[0] for point in att_cities_locations)
max_y = max(point[1] for point in att_cities_locations)
scale_x = (WIDTH - PLOT_X_OFFSET - NODE_RADIUS) / max_x
scale_y = HEIGHT / max_y
cities_locations = [(int(point[0] * scale_x + PLOT_X_OFFSET),
                     int(point[1] * scale_y)) for point in att_cities_locations]
target_solution = [cities_locations[i-1] for i in att_48_cities_order]
fitness_target_solution = calculate_fitness(target_solution)
print(f"Best Solution: {fitness_target_solution}")
# ----- Using att48 benchmark


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1
start_time = time.time()


# Create Initial Population
# TODO:- use some heuristic like Nearest Neighbour our Convex Hull to initialize
population = generate_random_population(cities_locations, POPULATION_SIZE)
best_fitness_values = []
best_solutions = []


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    generation = next(generation_counter)

    screen.fill(WHITE)

    population_fitness = [calculate_fitness(
        individual) for individual in population]

    population, population_fitness = sort_population(
        population,  population_fitness)

    best_fitness = calculate_fitness(population[0])
    best_solution = population[0]

    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    draw_plot(screen, list(range(len(best_fitness_values))),
              best_fitness_values, y_label="Fitness - Distance (pxls)")

    draw_cities(screen, cities_locations, RED, NODE_RADIUS)
    draw_paths(screen, best_solution, BLUE, width=3)
    draw_paths(screen, population[1], rgb_color=(128, 128, 128), width=1)

    print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")

    new_population = [population[0]]  # Keep the best individual: ELITISM

    while len(new_population) < POPULATION_SIZE:

        # selection
        # simple selection based on first 10 best solutions
        # parent1, parent2 = random.choices(population[:10], k=2)

        # solution based on fitness probability
        probability = 1 / np.array(population_fitness)
        parent1, parent2 = random.choices(population, weights=probability, k=2)

        # child1 = order_crossover(parent1, parent2)
        child1 = order_crossover(parent1, parent1)

        child1 = mutate(child1, MUTATION_PROBABILITY)

        new_population.append(child1)

    population = new_population

    pygame.display.flip()
    clock.tick(FPS)

    # check time limit
    elapsed = time.time() - start_time
    if elapsed >= TIME_LIMIT_SECONDS:
        print(f"Time limit reached ({TIME_LIMIT_SECONDS}s). Stopping...")
        running = False


# TODO: save the best individual in a file if it is better than the one saved.

# exit software
pygame.quit()

# After exiting main loop, save top 50 results to CSV
try:
    results = []
    for idx, fit in enumerate(best_fitness_values):
        sol = best_solutions[idx]
        gen = idx + 1
        results.append((fit, gen, sol))

    # sort by fitness (ascending) and take top 50
    results_sorted = sorted(results, key=lambda x: x[0])
    top_k = results_sorted[:50]

    csv_path = "top50_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "generation", "fitness", "route_json"])
        for rank, (fitness, generation, route) in enumerate(top_k, start=1):
            writer.writerow(
                [rank, generation, round(fitness, 6), json.dumps(route)])

    print(f"Top {len(top_k)} results saved to {csv_path}")
except Exception as e:
    print("Failed to write results CSV:", e)

# Also write a structured JSON with the top 50 results
try:
    json_path = "top50_results.json"
    json_list = []
    for rank, (fitness, generation, route) in enumerate(top_k, start=1):
        json_list.append({
            "rank": rank,
            "generation": generation,
            "fitness": round(fitness, 6),
            "route": route,
        })

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump({
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "time_limit_seconds": TIME_LIMIT_SECONDS,
            "count": len(json_list),
            "top_results": json_list,
        }, jf, indent=2, ensure_ascii=False)

    print(f"Top {len(json_list)} results saved to {json_path}")
except Exception as e:
    print("Failed to write results JSON:", e)

sys.exit()

# After exiting main loop, save top 50 results to CSV
try:
    results = []
    for idx, fit in enumerate(best_fitness_values):
        sol = best_solutions[idx]
        gen = idx + 1
        results.append((fit, gen, sol))

    # sort by fitness (ascending) and take top 50
    results_sorted = sorted(results, key=lambda x: x[0])
    top_k = results_sorted[:50]

    csv_path = "top50_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "generation", "fitness", "route_json"])
        for rank, (fitness, generation, route) in enumerate(top_k, start=1):
            writer.writerow(
                [rank, generation, round(fitness, 6), json.dumps(route)])

    print(f"Top {len(top_k)} results saved to {csv_path}")
except Exception as e:
    print("Failed to write results CSV:", e)
