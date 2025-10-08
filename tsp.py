import pygame
from pygame.locals import *
import random
import itertools
from genetic_algorithm import mutate, order_crossover, generate_random_population, calculate_fitness, sort_population, default_problems
from draw_functions import draw_paths, draw_plot, draw_cities, draw_text
import time
import csv
import json
import sys
import numpy as np
import pygame


# Define constant values
# pygame
WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450

# GA
N_CITIES = 15
# Garantir número mínimo de cidades
if N_CITIES < 20:
    print(f"N_CITIES ({N_CITIES}) menor que 20 — ajustando para 20")
    N_CITIES = 20
POPULATION_SIZE = 100
N_GENERATIONS = None
TIME_LIMIT_SECONDS = 10  # 2 minutes
MUTATION_PROBABILITY = 0.5

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Gera posições aleatórias de cidades dentro da área definida (respeitando margens)
# e garantindo um espaçamento mínimo entre cidades
MIN_CITY_DISTANCE = 30  # pixels, ajuste conforme necessário para espaçamento maior
cities_locations = []
max_attempts = 1000
attempts = 0
while len(cities_locations) < N_CITIES and attempts < max_attempts:
    attempts += 1
    x = random.randint(NODE_RADIUS + PLOT_X_OFFSET, WIDTH - NODE_RADIUS)
    y = random.randint(NODE_RADIUS, HEIGHT - NODE_RADIUS)
    pt = (x, y)
    # verificar distância mínima
    ok = True
    for ex in cities_locations:
        dx = ex[0] - x
        dy = ex[1] - y
        if (dx*dx + dy*dy) ** 0.5 < MIN_CITY_DISTANCE:
            ok = False
            break
    if ok:
        cities_locations.append(pt)

# Se não foi possível preencher por causa do espaço, preencher sem restrição
if len(cities_locations) < N_CITIES:
    for _ in range(len(cities_locations), N_CITIES):
        cities_locations.append((
            random.randint(NODE_RADIUS + PLOT_X_OFFSET, WIDTH - NODE_RADIUS),
            random.randint(NODE_RADIUS, HEIGHT - NODE_RADIUS)
        ))

# Cria uma ordem alvo aleatória (permutações dos índices das cidades)
target_order = list(range(len(cities_locations)))
random.shuffle(target_order)
target_solution = [cities_locations[i] for i in target_order]
fitness_target_solution = calculate_fitness(target_solution)
print(f"Best Solution (random target): {fitness_target_solution}")


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

# Antes de sair, salvar uma imagem PNG da melhor rota encontrada
try:
    if best_fitness_values and best_solutions:
        best_idx = int(np.argmin(best_fitness_values))
        best_route = best_solutions[best_idx]
        # criar surfaces: mapa (rota) e plot (fitness)
        map_surf = pygame.Surface((WIDTH - PLOT_X_OFFSET, HEIGHT))
        map_surf.fill(WHITE)
        # desenhar cidades e rota no mapa
        # ajustar coordenadas se cities_locations usam offset PLOT_X_OFFSET
        draw_cities(map_surf, [(x - PLOT_X_OFFSET, y)
                    for (x, y) in cities_locations], RED, NODE_RADIUS)
        # desenhar rota ajustando as coordenadas
        adjusted_route = [(x - PLOT_X_OFFSET, y) for (x, y) in best_route]
        draw_paths(map_surf, adjusted_route, BLUE, width=3)

        # criar surface do plot (usar draw_plot que desenha diretamente em uma surface do tamanho do plot)
        plot_width = PLOT_X_OFFSET
        plot_height = HEIGHT
        plot_surf = pygame.Surface((plot_width, plot_height))
        plot_surf.fill(WHITE)
        try:
            # draw_plot espera uma surface do pygame e desenha o gráfico nela
            draw_plot(plot_surf, list(range(len(best_fitness_values))),
                      best_fitness_values, y_label="Fitness - Distance (pxls)")
        except Exception:
            # fallback: deixar plot_surf em branco
            pass

        # combinar plot_surf (à esquerda) e map_surf (à direita)
        final_surf = pygame.Surface(
            (plot_width + map_surf.get_width(), HEIGHT))
        final_surf.fill(WHITE)
        final_surf.blit(plot_surf, (0, 0))
        final_surf.blit(map_surf, (plot_width, 0))

        image_path = "best_route.png"
        try:
            pygame.image.save(final_surf, image_path)
            print(f"Best route image saved to {image_path}")
        except Exception as e:
            print("Falha ao salvar imagem da melhor rota:", e)
        # --- Salvar imagens dos top-5 resultados (plot + mapa) ---
        try:
            # Construir lista de resultados (fitness, generation, route) a partir dos históricos
            results = []
            for idx, fit in enumerate(best_fitness_values):
                sol = best_solutions[idx]
                gen = idx + 1
                results.append((fit, gen, sol))

            results_sorted = sorted(results, key=lambda x: x[0])
            top5 = results_sorted[:5]

            for rank, (fitness, generation, route) in enumerate(top5, start=1):
                # criar mapa da rota
                map_width = WIDTH - PLOT_X_OFFSET
                map_surf2 = pygame.Surface((map_width, HEIGHT))
                map_surf2.fill(WHITE)
                # desenhar cidades e rota (ajustando X pelo offset)
                draw_cities(map_surf2, [(x - PLOT_X_OFFSET, y) for (x, y) in cities_locations], RED, NODE_RADIUS)
                adjusted_route2 = [(x - PLOT_X_OFFSET, y) for (x, y) in route]
                draw_paths(map_surf2, adjusted_route2, BLUE, width=3)

                # criar plot
                plot_w = PLOT_X_OFFSET
                plot_h = HEIGHT
                plot_surf2 = pygame.Surface((plot_w, plot_h))
                plot_surf2.fill(WHITE)
                try:
                    draw_plot(plot_surf2, list(range(len(best_fitness_values))), best_fitness_values, y_label="Fitness - Distance (pxls)")
                except Exception:
                    pass

                # combinar e anotar com texto
                combined = pygame.Surface((plot_w + map_width, HEIGHT))
                combined.fill(WHITE)
                combined.blit(plot_surf2, (0, 0))
                combined.blit(map_surf2, (plot_w, 0))

                # desenhar texto descritivo
                try:
                    txt = f"Rank {rank} - Gen {generation} - Fitness {round(fitness,6)}"
                    draw_text(combined, txt, BLACK, position=(10, 10))
                except Exception:
                    pass

                out_path = f"top{rank}_route.png"
                try:
                    pygame.image.save(combined, out_path)
                    print(f"Saved top-{rank} image: {out_path}")
                except Exception as e:
                    print(f"Failed to save top-{rank} image:", e)
        except Exception as e:
            print("Erro ao salvar imagens top-5:", e)
except Exception as e:
    print("Erro ao gerar imagem da melhor rota:", e)

# exit software
pygame.quit()

# After exiting main loop, save top 50 results to CSV
try:
    results = []
    for idx, fit in enumerate(best_fitness_values):
        sol = best_solutions[idx]
        gen = idx + 1
        results.append((fit, gen, sol))

    # sort by fitness (ascending) and take top 20
    results_sorted = sorted(results, key=lambda x: x[0])
    top_k = results_sorted[:20]

    csv_path = "top20_results.csv"
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
    json_path = "top20_results.json"
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
    top_k = results_sorted[:20]

    csv_path = "top20_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "generation", "fitness", "route_json"])
        for rank, (fitness, generation, route) in enumerate(top_k, start=1):
            writer.writerow(
                [rank, generation, round(fitness, 6), json.dumps(route)])

    print(f"Top {len(top_k)} results saved to {csv_path}")
except Exception as e:
    print("Failed to write results CSV:", e)
