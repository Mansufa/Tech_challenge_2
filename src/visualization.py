from typing import List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg

from config import GREEN, PRIORITY_COLORS, RED, VEHICLE_COLORS
from models import Delivery, Priority

matplotlib.use("Agg")


def draw_deliveries(screen: pygame.Surface, deliveries: List[Delivery], radius: int):
    for i, delivery in enumerate(deliveries):
        if i == 0:
            # Primeira entrega em verde (depósito/ponto inicial)
            pygame.draw.circle(screen, GREEN, delivery.location, radius + 2)
        else:
            # Cor baseada na prioridade
            color = PRIORITY_COLORS.get(delivery.priority, RED)
            pygame.draw.circle(screen, color, delivery.location, radius)


def draw_plot(
    screen: pygame.Surface,
    x_values: List[int],
    y_values: List[float],
    x_label: str = "Geração",
    y_label: str = "Distância (px)",
):
    if len(y_values) < 2:
        return

    # Cria figura do matplotlib
    fig, ax = plt.subplots(figsize=(4.5, 4), dpi=100)
    ax.plot(x_values, y_values, color="#1f77b4", linewidth=2)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title("Evolução do Fitness")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    # Converte matplotlib para pygame surface
    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    width, height = canvas.get_width_height()

    # Obtém dados RGB do canvas
    raw_data = None
    if hasattr(canvas, "tostring_rgb"):
        try:
            raw_data = canvas.tostring_rgb()
        except Exception:
            raw_data = None

    if raw_data is None and hasattr(canvas, "buffer_rgba"):
        buf = canvas.buffer_rgba()
        arr = np.frombuffer(buf, dtype=np.uint8)
        try:
            arr = arr.reshape((height, width, 4))
        except Exception:
            arr = arr.reshape((width, height, 4)).transpose((1, 0, 2))

        arr = arr[:, :, :3]
        raw_data = arr.tobytes()

    if raw_data is None:
        raise RuntimeError("Não foi possível extrair dados RGB do matplotlib")

    size = (width, height)
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0, 0))

    plt.close(fig)


def draw_multiple_routes(screen: pygame.Surface, vehicle_routes: List[List[Delivery]], depot: Tuple[int, int]):
    try:
        font = pygame.font.SysFont("Arial", 14)
    except Exception:
        font = pygame.font.SysFont("Arial", 14)

    # Desenha cada rota com cor diferente
    for idx, route in enumerate(vehicle_routes):
        if not route:
            continue

        color = VEHICLE_COLORS[idx % len(VEHICLE_COLORS)]

        first_delivery = route[0]
        pygame.draw.line(screen, color, depot, first_delivery.location, 2)

        for i in range(len(route) - 1):
            start = route[i].location
            end = route[i + 1].location
            pygame.draw.line(screen, color, start, end, 2)

        last_delivery = route[-1]
        pygame.draw.line(screen, color, last_delivery.location, depot, 2)

        for position, delivery in enumerate(route, start=1):
            text = font.render(str(position), True, (0, 0, 0))
            text_rect = text.get_rect(center=delivery.location)

            screen.blit(text, text_rect)


def draw_depot(screen: pygame.Surface, depot: Tuple[int, int], radius: int = 10):
    pygame.draw.circle(screen, GREEN, depot, radius + 4)
    pygame.draw.circle(screen, (0, 0, 0), depot, radius + 4, 2)  # Borda preta


def draw_legend(screen: pygame.Surface, x: int = 450, y: int = 300):
    font = pygame.font.Font(None, 12)

    items = [
        (Priority.CRITICAL, "CRÍTICA"),
        (Priority.HIGH, "ALTA"),
        (Priority.MEDIUM, "MÉDIA"),
        (Priority.LOW, "BAIXA"),
        (None, "DEPÓSITO"),
    ]

    for i, (priority, label) in enumerate(items):
        pos_y = y + 5 + (i * 17)
        color = GREEN if priority is None else PRIORITY_COLORS.get(priority, RED)

        pygame.draw.circle(screen, color, (x + 10, pos_y + 6), 4)

        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (x + 20, pos_y))
