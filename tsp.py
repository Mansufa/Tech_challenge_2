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
import argparse


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
TIME_LIMIT_SECONDS = 60  # 1 minute
MUTATION_PROBABILITY = 0.5

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ROUTE_COLORS = [(BLUE), (0, 150, 0), (255, 165, 0),
                (128, 128, 128), (0, 150, 150), (150, 0, 0)]


def get_route_color(idx: int):
    return ROUTE_COLORS[idx % len(ROUTE_COLORS)]


def draw_marker(surface: pygame.Surface, pos: tuple, label: str, color: tuple, radius: int = 8, font_size: int = 12):
    """Draw a filled circle and centered label at pos (used to number visited cities)."""
    try:
        x, y = int(pos[0]), int(pos[1])
        pygame.draw.circle(surface, color, (x, y), radius)
        text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
        font = pygame.font.SysFont('Arial', font_size)
        txt_surf = font.render(label, True, text_color)
        txt_rect = txt_surf.get_rect(center=(x, y))
        surface.blit(txt_surf, txt_rect)
    except Exception:
        pass


def draw_legend(surface: pygame.Surface, vehicle_count: int, topleft: tuple, font_size: int = 14, box_size: int = 16, include_depot: bool = True):
    """Draw a legend with vehicle colors and depot label at topleft."""
    try:
        font = pygame.font.SysFont('Arial', font_size)
        x0, y0 = topleft
        entries = min(vehicle_count, len(ROUTE_COLORS))
        for v in range(entries):
            col = get_route_color(v)
            pygame.draw.rect(surface, col, (x0, y0 + v *
                             (box_size + 6), box_size, box_size))
            label = f"Veículo {v+1}"
            txt = font.render(label, True, BLACK)
            surface.blit(txt, (x0 + box_size + 6, y0 + v * (box_size + 6)))
        if include_depot:
            depot_y = y0 + entries * (box_size + 6)
            pygame.draw.rect(
                surface, PURPLE, (x0, depot_y, box_size, box_size))
            txt = font.render("Depot", True, BLACK)
            surface.blit(txt, (x0 + box_size + 6, depot_y))
    except Exception:
        pass


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

# Definir uma cidade de origem (depot) fixa: usamos a primeira cidade gerada como origem
# e removemos ela da lista de cidades que serão permutadas pelo algoritmo.
if cities_locations:
    depot = cities_locations.pop(0)
else:
    # fallback: se por alguma razão não há cidades, criar um depot no centro
    depot = (PLOT_X_OFFSET + (WIDTH - PLOT_X_OFFSET) // 2, HEIGHT // 2)

# Cria uma ordem alvo aleatória (permutações dos índices das cidades)
target_order = list(range(len(cities_locations)))
random.shuffle(target_order)
target_solution = [cities_locations[i] for i in target_order]
# A mensagem sobre target será calculada após o usuário informar a quantidade de veículos
fitness_target_solution = None


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1
start_time = time.time()


def ask_for_vehicle_count(screen, clock, default=1):
    """Simple Pygame text input to ask the user for number of vehicles."""
    font = pygame.font.SysFont('Arial', 24)
    input_str = str(default)
    asking = True
    while asking:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    asking = False
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                else:
                    ch = event.unicode
                    if ch.isdigit():
                        input_str += ch

        screen.fill(WHITE)
        prompt = font.render(
            'Quantidade de veículos (enter para confirmar):', True, BLACK)
        val_surf = font.render(input_str, True, (50, 50, 200))
        screen.blit(prompt, (20, 100))
        screen.blit(val_surf, (20, 140))
        pygame.display.flip()
        clock.tick(30)

    try:
        val = int(input_str)
        if val < 1:
            val = 1
    except Exception:
        val = default
    return val


def ask_for_parameters(screen, clock, default_vehicles=1, default_capacity=10, default_max_distance=10, default_priority=1.0):
    """Ask sequentially for number of vehicles, capacity and max distance using Pygame input.

    Returns a tuple: (vehicles:int, capacity:float, max_distance:float)
    """
    def ask(prompt_text, default_value, is_float=False):
        font = pygame.font.SysFont('Arial', 24)
        input_str = str(default_value)
        asking = True
        while asking:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        asking = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_str = input_str[:-1]
                    else:
                        ch = event.unicode
                        # accept digits and one dot for floats
                        if ch.isdigit() or (is_float and ch == '.' and '.' not in input_str):
                            input_str += ch

            screen.fill(WHITE)
            prompt = font.render(prompt_text, True, BLACK)
            val_surf = font.render(input_str, True, (50, 50, 200))
            screen.blit(prompt, (20, 100))
            screen.blit(val_surf, (20, 140))
            pygame.display.flip()
            clock.tick(30)

        try:
            if is_float:
                return float(input_str)
            else:
                v = int(input_str)
                return v if v >= 1 else 1
        except Exception:
            return default_value

    vehicles = ask('Quantidade de veículos (enter para confirmar):',
                   default_vehicles, is_float=False)
    capacity = ask('Capacidade máxima por veículo (enter para confirmar):',
                   default_capacity, is_float=False)
    max_distance = ask('Distância máxima por veículo (enter para confirmar):',
                       default_max_distance, is_float=True)
    priority = ask('Prioridade padrão por cidade (ex: 1.0):',
                   default_priority, is_float=True)

    return vehicles, capacity, max_distance, priority


# Allow passing parameters via CLI. If all provided we skip prompts; otherwise use provided values as defaults.
parser = argparse.ArgumentParser(
    description='TSP demo (optional CLI parameters to skip prompts)')
parser.add_argument('--vehicles', type=int, help='number of vehicles')
parser.add_argument('--capacity', type=float, help='capacity per vehicle')
parser.add_argument('--max-distance', type=float,
                    help='max distance per vehicle')
parser.add_argument('--priority', type=float, help='default priority per city')
args = parser.parse_args()

if args.vehicles is not None and args.capacity is not None and args.max_distance is not None and args.priority is not None:
    VEHICLE_COUNT = args.vehicles
    CAPACITY = args.capacity
    MAX_DISTANCE = args.max_distance
    PRIORITY = args.priority
else:
    default_vehicles = args.vehicles if args.vehicles is not None else 1
    default_capacity = args.capacity if args.capacity is not None else 10
    default_max_distance = args.max_distance if args.max_distance is not None else 1000
    default_priority = args.priority if args.priority is not None else 1.0
    VEHICLE_COUNT, CAPACITY, MAX_DISTANCE, PRIORITY = ask_for_parameters(
        screen, clock, default_vehicles=default_vehicles, default_capacity=default_capacity, default_max_distance=default_max_distance, default_priority=default_priority)

print(
    f"Usando VEHICLE_COUNT = {VEHICLE_COUNT}, CAPACITY = {CAPACITY}, MAX_DISTANCE = {MAX_DISTANCE}, PRIORITY = {PRIORITY}")

# Agora que sabemos VEHICLE_COUNT, calcular o fitness do target (opcional)
try:
    fitness_target_solution = calculate_fitness(
        target_solution, depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(target_solution))
    print(f"Best Solution (random target): {fitness_target_solution}")
except Exception:
    fitness_target_solution = None


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

    # Evaluate individuals as TSP routes that start and end at the depot
    population_fitness = [calculate_fitness(
        individual, depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(individual)) for individual in population]

    population, population_fitness = sort_population(
        population,  population_fitness)

    best_fitness = calculate_fitness(
        population[0], depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(population[0]))
    best_solution = population[0]

    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    draw_plot(screen, list(range(len(best_fitness_values))),
              best_fitness_values, y_label="Fitness - Distance (pxls)")

    # Desenhar depot (origem) e demais cidades (cities_locations contém apenas cidades, sem o depot)
    try:
        # depot pode estar fora do espaço plotado, mas foi gerado com offset
        pygame.draw.circle(screen, PURPLE, depot, NODE_RADIUS + 2)
    except Exception:
        pass

    draw_cities(screen, [(x, y)
                for (x, y) in cities_locations], (140, 140, 140), NODE_RADIUS)

    # Mostrar as rotas por veículo (numeradas) para a melhor solução
    try:
        if best_solution:
            fitness_val, best_routes = calculate_fitness(
                best_solution, depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(best_solution), return_routes=True)
            for v_idx, route_indices in enumerate(best_routes):
                color = get_route_color(v_idx)
                coords = [depot] + [best_solution[i]
                                    for i in route_indices] + [depot]
                draw_paths(screen, coords, color, width=3 if v_idx == 0 else 2)
                # markers numbered
                for order_idx, city_idx in enumerate(route_indices, start=1):
                    draw_marker(screen, best_solution[city_idx], str(
                        order_idx), color, radius=10, font_size=12)
            # legenda posicionada abaixo da área do mapa (embaixo das rotas)
            try:
                entries = min(VEHICLE_COUNT, len(ROUTE_COLORS))
                box_size = 16
                include_depot = True
                total_h = entries * (box_size + 6) + \
                    (box_size + 6 if include_depot else 0)
                legend_x = PLOT_X_OFFSET + 10
                legend_y = HEIGHT - total_h - 30
                draw_legend(screen, VEHICLE_COUNT, (legend_x, legend_y),
                            font_size=14, box_size=box_size, include_depot=include_depot)
            except Exception:
                pass
    except Exception:
        pass

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
        child1 = order_crossover(parent1, parent2)

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
        # desenhar depot e cidades no mapa (map_surf usa coordenadas sem o offset)
        depot_map = (depot[0] - PLOT_X_OFFSET, depot[1])
        draw_cities(map_surf, [depot_map], PURPLE, NODE_RADIUS + 2)
        draw_cities(map_surf, [(x - PLOT_X_OFFSET, y)
                    for (x, y) in cities_locations], (140, 140, 140), NODE_RADIUS)
        # desenhar rotas por veículo e markers no mapa salvo
        try:
            _, best_routes = calculate_fitness(
                best_route, depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(best_route), return_routes=True)
            for v_idx, route_indices in enumerate(best_routes):
                color = get_route_color(v_idx)
                coords = [depot_map] + [(best_route[i][0] - PLOT_X_OFFSET, best_route[i][1])
                                        for i in route_indices] + [depot_map]
                draw_paths(map_surf, coords, color,
                           width=3 if v_idx == 0 else 2)
                for order_idx, city_idx in enumerate(route_indices, start=1):
                    c = best_route[city_idx]
                    draw_marker(map_surf, (c[0] - PLOT_X_OFFSET, c[1]),
                                str(order_idx), color, radius=10, font_size=14)
            # legenda na surface do plot será desenhada depois na final_surf
        except Exception:
            adjusted_route = [depot_map] + [(x - PLOT_X_OFFSET, y)
                                            for (x, y) in best_route] + [depot_map]
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
        # desenhar legenda na combined antes de salvar
        try:
            # place legend below the map area inside the combined final surface
            entries = min(VEHICLE_COUNT, len(ROUTE_COLORS))
            box_size = 18
            include_depot = True
            total_h = entries * (box_size + 6) + \
                (box_size + 6 if include_depot else 0)
            legend_x = plot_width + 10
            legend_y = HEIGHT - total_h - 10
            draw_legend(final_surf, VEHICLE_COUNT, (legend_x, legend_y),
                        font_size=16, box_size=box_size, include_depot=include_depot)
        except Exception:
            pass

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
                # desenhar depot e cidades no mapa do top-K
                depot_map2 = (depot[0] - PLOT_X_OFFSET, depot[1])
                draw_cities(map_surf2, [depot_map2], PURPLE, NODE_RADIUS + 2)
                draw_cities(map_surf2, [(x - PLOT_X_OFFSET, y)
                            for (x, y) in cities_locations], (140, 140, 140), NODE_RADIUS)
                try:
                    _, routes_k = calculate_fitness(
                        route, depot=depot, vehicle_count=VEHICLE_COUNT, capacity=CAPACITY, max_distance=MAX_DISTANCE, priorities=[PRIORITY]*len(route), return_routes=True)
                    for v_idx, r_inds in enumerate(routes_k):
                        color_k = get_route_color(v_idx)
                        coords_k = [
                            depot_map2] + [(route[i][0] - PLOT_X_OFFSET, route[i][1]) for i in r_inds] + [depot_map2]
                        draw_paths(map_surf2, coords_k, color_k, width=2)
                        for order_idx, city_idx in enumerate(r_inds, start=1):
                            c = route[city_idx]
                            draw_marker(
                                map_surf2, (c[0] - PLOT_X_OFFSET, c[1]), str(order_idx), color_k, radius=10, font_size=14)
                except Exception:
                    adjusted_route2 = [
                        depot_map2] + [(x - PLOT_X_OFFSET, y) for (x, y) in route] + [depot_map2]
                    draw_paths(map_surf2, adjusted_route2, BLUE, width=3)

                # criar plot
                plot_w = PLOT_X_OFFSET
                plot_h = HEIGHT
                plot_surf2 = pygame.Surface((plot_w, plot_h))
                plot_surf2.fill(WHITE)
                try:
                    draw_plot(plot_surf2, list(range(len(best_fitness_values))),
                              best_fitness_values, y_label="Fitness - Distance (pxls)")
                except Exception:
                    pass

                # combinar e anotar com texto
                combined = pygame.Surface((plot_w + map_width, HEIGHT))
                combined.fill(WHITE)
                combined.blit(plot_surf2, (0, 0))
                combined.blit(map_surf2, (plot_w, 0))

                # desenhar texto descritivo
                try:
                    txt = f"Rank {rank} - Gen {generation} - Fitness {round(fitness, 6)}"
                    draw_text(combined, txt, BLACK, position=(10, 10))
                except Exception:
                    pass

                # desenhar legenda na combined antes de salvar
                try:
                    # place legend below the map area in the combined top-K image
                    entries_k = min(VEHICLE_COUNT, len(ROUTE_COLORS))
                    box_k = 16
                    include_depot_k = True
                    total_h_k = entries_k * \
                        (box_k + 6) + (box_k + 6 if include_depot_k else 0)
                    legend_x_k = plot_w + 10
                    legend_y_k = HEIGHT - total_h_k - 10
                    draw_legend(combined, VEHICLE_COUNT, (legend_x_k, legend_y_k),
                                font_size=14, box_size=box_k, include_depot=include_depot_k)
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
