import os
import random
import time

import numpy as np
import pygame
import csv

from cities import generate_deliveries, generate_vehicle_capacities, generate_vehicle_max_deliveries
from config import (
    FLEET_CAPACITY_MARGIN,
    FPS,
    HEIGHT,
    MUTATION_PROBABILITY,
    N_CITIES,
    NODE_RADIUS,
    NUM_VEHICLES,
    POPULATION_SIZE,
    TIME_LIMIT_SECONDS,
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


def get_inputs_via_pygame(defaults):
    """Abre uma janela Pygame simples para o usuário digitar 3 valores na ordem:
    N_CITIES (int), NUM_VEHICLES (int), TIME_LIMIT_SECONDS (float).
    Pressione Enter para submeter. Campos vazios usam os defaults.
    Retorna tuple (n_cities, num_vehicles, time_limit_seconds).
    """
    pygame.init()
    win_w, win_h = 640, 260
    win = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Configurações - VRP")
    font = pygame.font.Font(None, 28)
    small = pygame.font.Font(None, 20)

    labels = [
        ("Numero de cidades", str(defaults[0]), "int"),
        ("Quantidade de Veiculos", str(defaults[1]), "int"),
        ("Tempo de execução (segundos)", str(defaults[2]), "float"),
    ]

    inputs = [list(x[1]) if x[1] else [] for x in labels]
    types = [x[2] for x in labels]
    active = [False, False, False]
    active[0] = True

    message = "Digite valores e pressione Enter (Esc para cancelar - usa defaults)"
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                return defaults
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    return defaults
                if event.key == pygame.K_TAB:
                    idx = active.index(True)
                    active[idx] = False
                    active[(idx + 1) % 3] = True
                elif event.key == pygame.K_RETURN:
                    values = []
                    ok = True
                    for i, chars in enumerate(inputs):
                        s = ''.join(chars).strip()
                        if s == "":
                            values.append(defaults[i])
                            continue
                        try:
                            if types[i] == "int":
                                v = int(float(s))
                                if v <= 0:
                                    raise ValueError()
                                values.append(v)
                            else:
                                v = float(s)
                                if v < 0.1:
                                    raise ValueError()
                                values.append(v)
                        except Exception:
                            message = f"Valor inválido para {labels[i][0]}: '{s}'"
                            ok = False
                            break
                    if ok:
                        pygame.display.quit()
                        return tuple(values)
                else:
                    for i, a in enumerate(active):
                        if a:
                            if event.key == pygame.K_BACKSPACE:
                                if inputs[i]:
                                    inputs[i].pop()
                            else:
                                ch = event.unicode
                                if ch.isdigit() or (ch == '.' and types[i] == 'float'):
                                    inputs[i].append(ch)
                            break

        win.fill((245, 245, 245))
        title = font.render("Parâmetros da simulação", True, (10, 10, 10))
        win.blit(title, (20, 10))

        info = small.render(message, True, (80, 80, 80))
        win.blit(info, (20, 44))

        for i, (label, default, _) in enumerate(labels):
            y = 80 + i * 44
            lbl = small.render(
                f"{label} (padrão {default}):", True, (20, 20, 20))
            win.blit(lbl, (20, y))

            rect = pygame.Rect(300, y - 6, 140, 30)
            pygame.draw.rect(win, (255, 255, 255), rect)
            pygame.draw.rect(win, (0, 0, 0) if active[i] else (
                120, 120, 120), rect, 2)

            txt = ''.join(inputs[i]) if inputs[i] else ''
            txt_surf = small.render(txt, True, (0, 0, 0))
            win.blit(txt_surf, (rect.x + 6, rect.y + 6))

        hint = small.render(
            "Tab para alternar campos. Enter para confirmar.", True, (80, 80, 80))
        win.blit(hint, (20, win_h - 40))

        pygame.display.flip()
        clock.tick(30)


# Abre a janela de input e recebe valores (usar defaults definidos em config)
n_cities, num_vehicles, time_limit_seconds = get_inputs_via_pygame(
    (N_CITIES, NUM_VEHICLES, TIME_LIMIT_SECONDS))

deliveries = generate_deliveries(num_deliveries=n_cities)
print(f"Entregas geradas: {len(deliveries)}")

total_weight = sum(d.weight for d in deliveries)

vehicle_capacities = generate_vehicle_capacities(
    total_weight, num_vehicles, FLEET_CAPACITY_MARGIN)
total_capacity = sum(vehicle_capacities)

vehicle_max_deliveries = generate_vehicle_max_deliveries(
    n_cities, num_vehicles)

print(f"\nVeículos disponíveis: {num_vehicles}")
for i, (capacity, max_deliveries) in enumerate(zip(vehicle_capacities, vehicle_max_deliveries, strict=False), 1):
    print(f"  V{i}: Capacidade = {capacity:.1f}kg, Máx. Entregas = {max_deliveries}")

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


start_time = time.time()
while (time.time() - start_time) < time_limit_seconds:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    generation += 1

    screen.fill(WHITE)

    population_fitness = [
        calculate_fitness_multi_vehicle(
            individual, num_vehicles, DEPOT_LOCATION, vehicle_capacities, vehicle_max_deliveries
        )
        for individual in population
    ]

    population, population_fitness = sort_population(
        population, population_fitness)

    best_fitness = population_fitness[0]
    best_solution = population[0]
    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    draw_plot(screen, list(range(1, len(best_fitness_values) + 1)),
              best_fitness_values)

    best_routes = split_deliveries_by_vehicle(
        best_solution, num_vehicles, DEPOT_LOCATION, vehicle_capacities, vehicle_max_deliveries
    )

    draw_deliveries(screen, deliveries, NODE_RADIUS)

    draw_depot(screen, DEPOT_LOCATION, NODE_RADIUS)

    draw_multiple_routes(screen, best_routes, DEPOT_LOCATION)

    stats_lines = []
    for vehicle_id, route in enumerate(best_routes, 1):
        route_load = sum(d.weight for d in route)
        route_distance = calculate_route_distance(route, DEPOT_LOCATION)

        # Capacidade específica deste veículo
        vehicle_capacity = vehicle_capacities[vehicle_id - 1]
        max_deliveries = vehicle_max_deliveries[vehicle_id - 1]

        overload = max(0, route_load - vehicle_capacity)
        exceed_deliveries = max(0, len(route) - max_deliveries)

        vehicle_stats = (
            f"V{vehicle_id}: {len(route)}/{max_deliveries} entregas, {round(route_load, 1)}kg/{round(vehicle_capacity, 1)}kg, "
            f"{round(route_distance, 0)}dist"
        )
        stats_lines.append(vehicle_stats)

    print(f"Geração {generation}: Fitness = {round(best_fitness, 2)} | " +
          " | ".join(stats_lines))

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

best_route = best_solutions[best_fitness_values.index(
    min(best_fitness_values))]
best_vehicle_routes = split_deliveries_by_vehicle(
    best_route, num_vehicles, DEPOT_LOCATION, vehicle_capacities, vehicle_max_deliveries
)

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
    max_deliveries = vehicle_max_deliveries[vehicle_id - 1]

    print(f"\nVeículo {vehicle_id}:")
    print(f"  Capacidade do veículo: {vehicle_capacity:.2f}kg")
    print(f"  Entregas: {len(route)} / {max_deliveries}")
    print(f"  Carga: {route_load:.2f}kg / {vehicle_capacity:.2f}kg")
    print(f"  Distância: {route_distance:.0f}")

    if route:
        print("  Primeiras entregas:")
        for i, delivery in enumerate(route[:5], 1):
            print(
                f"    {i}. Prioridade {delivery.priority.name} - {delivery.weight}kg")


print("\n" + "=" * 60)
print("SALVANDO TOP 5 MELHORES SOLUÇÕES")
print("=" * 60)

images_dir = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(images_dir, exist_ok=True)

# Pixels extras adicionados abaixo do mapa nas imagens salvas para colocar a legenda
SAVE_EXTRA_HEIGHT = 120

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
    # Atualiza o display para visualização
    screen.fill(WHITE)

    # Divide entregas entre veículos
    vehicle_routes = split_deliveries_by_vehicle(
        solution, num_vehicles, DEPOT_LOCATION, vehicle_capacities, vehicle_max_deliveries
    )

    # Desenha no display (tela)
    draw_plot(screen, list(range(1, len(best_fitness_values) + 1)),
              best_fitness_values)
    draw_deliveries(screen, deliveries, NODE_RADIUS)
    draw_depot(screen, DEPOT_LOCATION, NODE_RADIUS)
    draw_multiple_routes(screen, vehicle_routes, DEPOT_LOCATION)
    # Não desenhar a legenda na tela durante a execução interativa.
    # A legenda será adicionada somente nas imagens salvas (save_surface).

    # Adiciona texto com informações da solução no display
    font = pygame.font.Font(None, 28)
    title_text = font.render(
        f"Top {rank} - Fitness: {fitness:.2f}", True, (0, 0, 0))
    screen.blit(title_text, (10, 10))

    pygame.display.flip()

    # Cria uma superfície maior para salvar a imagem sem sobreposição da legenda
    save_surface = pygame.Surface((WIDTH, HEIGHT + SAVE_EXTRA_HEIGHT))
    save_surface.fill(WHITE)

    # Desenha o mapa/rotas na parte superior da imagem salva
    draw_plot(save_surface, list(
        range(1, len(best_fitness_values) + 1)), best_fitness_values)
    draw_deliveries(save_surface, deliveries, NODE_RADIUS)
    draw_depot(save_surface, DEPOT_LOCATION, NODE_RADIUS)
    draw_multiple_routes(save_surface, vehicle_routes, DEPOT_LOCATION)

    # Desenha a legenda deslocada para a área extra (abaixo do mapa)
    legend_y = HEIGHT + 10
    draw_legend(save_surface, x=20, y=legend_y, num_vehicles=num_vehicles)

    # Adiciona título na imagem salva
    font2 = pygame.font.Font(None, 28)
    title_text2 = font2.render(
        f"Top {rank} - Fitness: {fitness:.2f}", True, (0, 0, 0))
    save_surface.blit(title_text2, (10, 10))

    filename = f"top_{rank}.png"
    filepath = os.path.join(images_dir, filename)
    pygame.image.save(save_surface, filepath)

    print(f"✓ Salva: {filename} - Fitness: {fitness:.2f}")

    # Escreve um CSV com as rotas desta solução (um arquivo por imagem)
    csv_filename = f"top_{rank}.csv"
    csv_path = os.path.join(images_dir, csv_filename)

    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Cabeçalho
            writer.writerow([
                "SolutionRank",
                "Fitness",
                "VehicleID",
                "DeliveryIDs",
                "NumDeliveries",
                "TotalWeight",
                "Distance",
                "Priorities",
            ])

            for vid, route in enumerate(vehicle_routes, 1):
                delivery_ids = ";".join(str(d.id) for d in route)
                num_deliveries = len(route)
                total_w = round(sum(d.weight for d in route), 2)
                try:
                    dist = calculate_route_distance(route, DEPOT_LOCATION)
                except Exception:
                    dist = 0
                priorities = ";".join(d.priority.name for d in route)

                writer.writerow([
                    rank,
                    f"{fitness:.2f}",
                    vid,
                    delivery_ids,
                    num_deliveries,
                    f"{total_w:.2f}",
                    dist,
                    priorities,
                ])
    except Exception as e:
        print(f"Aviso: não foi possível salvar CSV {csv_filename}: {e}")

pygame.quit()
