from typing import List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg

from config import GREEN, PRIORITY_COLORS, RED, VEHICLE_COLORS, NUM_VEHICLES
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
    save_path: str | None = None,
):
    if len(y_values) < 2:
        return

    # Cria figura do matplotlib
    fig, ax = plt.subplots(figsize=(4.5, 4), dpi=100)
    ax.plot(x_values, y_values, color="#1f77b4", linewidth=2)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # Ajusta título com padding para criar margem entre o título e o gráfico
    ax.set_title("Evolução do Fitness", pad=14)
    ax.grid(True, alpha=0.3)
    # Usa tight_layout com um padding maior para evitar cortes
    plt.tight_layout(pad=2.0)

    # Salva a figura em arquivo se solicitado (antes de extrair dados do canvas)
    if save_path:
        try:
            fig.savefig(save_path, dpi=100)
        except Exception:
            # não falha a execução se o salvamento não funcionar
            pass

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


def draw_legend(screen: pygame.Surface, x: int | None = None, y: int | None = None):
    # Torna a legenda responsiva ao tamanho da janela
    screen_width, screen_height = screen.get_size()

    # Posição padrão no canto inferior direito com margem
    margin = max(10, int(min(screen_width, screen_height) * 0.02))
    if x is None:
        x = screen_width - int(screen_width * 0.45) - margin
    if y is None:
        y = margin + 20

    # Fontes escaladas com base na largura da janela
    base_font_size = max(12, int(screen_width / 80))
    title_font = pygame.font.Font(None, base_font_size + 4)
    font = pygame.font.Font(None, base_font_size)

    items = [
        (Priority.CRITICAL, "CRÍTICA"),
        (Priority.HIGH, "ALTA"),
        (Priority.MEDIUM, "MÉDIA"),
        (Priority.LOW, "BAIXA"),
        (None, "DEPÓSITO"),
    ]

    # Calcula tamanho estimado da caixa de legenda (duas colunas) responsivo
    line_height = int(base_font_size * 1.5)
    left_lines = len(items) + 1
    right_lines = max(1, NUM_VEHICLES)
    total_lines = max(left_lines, right_lines)
    box_height = int((total_lines * line_height) + margin)
    box_width = int(min(screen_width * 0.48, 420))

    # Desenha retângulo de fundo semi-transparente usando Surface com alpha
    bg_rect = pygame.Rect(x - 8, y - 8, box_width, box_height)
    try:
        overlay = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        overlay.fill((250, 250, 250, 220))  # branco levemente translúcido
        screen.blit(overlay, (bg_rect.x, bg_rect.y))
        pygame.draw.rect(screen, (160, 160, 160), bg_rect, 1)  # borda
    except Exception:
        # fallback sólido se Surface alpha não suportado
        pygame.draw.rect(screen, (245, 245, 245), bg_rect)
        pygame.draw.rect(screen, (180, 180, 180), bg_rect, 1)

    # Título da legenda
    title = title_font.render("Legenda", True, (0, 0, 0))
    screen.blit(title, (x + 8, y - 6))

    # Coordenadas base para colunas (ajustadas para o tamanho da caixa)
    left_x = x + 8
    right_x = x + int(box_width * 0.5) + 8

    # Itens de prioridade (coluna esquerda)
    for i, (priority, label) in enumerate(items):
        pos_y = y + (i * line_height) + 8
        color = GREEN if priority is None else PRIORITY_COLORS.get(priority, RED)

        pygame.draw.circle(screen, color, (left_x + 8, pos_y + int(line_height / 2)), int(base_font_size * 0.45))

        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (left_x + 26, pos_y))

    # Cabeçalho das rotas/veículos (coluna direita)
    vehicle_header = font.render("Rotas / Veículos:", True, (0, 0, 0))
    screen.blit(vehicle_header, (right_x, y + 2))

    # Desenha cada veículo com uma linha colorida e um marcador (coluna direita)
    for i in range(NUM_VEHICLES):
        pos_y = y + 18 + (i * line_height)
        color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]

        # Linha de exemplo da rota
        pygame.draw.line(screen, color, (right_x + 6, pos_y + int(line_height / 2)), (right_x + 36, pos_y + int(line_height / 2)), max(2, int(base_font_size / 3)))
        # Marcador circular no início da linha
        pygame.draw.circle(screen, color, (right_x + 6, pos_y + int(line_height / 2)), max(3, int(base_font_size / 2)))

        text = font.render(f"Veículo {i+1}", True, (0, 0, 0))
        screen.blit(text, (right_x + 44, pos_y))
