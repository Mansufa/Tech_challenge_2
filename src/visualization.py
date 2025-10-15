from typing import List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg

import math
from config import GREEN, PRIORITY_COLORS, RED, VEHICLE_COLORS
from models import Delivery, Priority

matplotlib.use("Agg")


def draw_deliveries(screen: pygame.Surface, deliveries: List[Delivery], radius: int):
    # Desenha todas as cidades usando somente as cores definidas em PRIORITY_COLORS.
    # O depósito deve ser desenhado explicitamente por draw_depot quando necessário.
    for delivery in deliveries:
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
    # Desenha cada rota com cor diferente. Se a rota estiver vazia, desenha um marcador
    # próximo ao depósito identificando o veículo (para mostrar veículos vazios).
    num_vehicles = len(vehicle_routes)
    offset_radius = 26
    for idx, route in enumerate(vehicle_routes):
        color = VEHICLE_COLORS[idx % len(VEHICLE_COLORS)]

        if not route:
            # Desenha um pequeno traço saindo do depósito para indicar veículo vazio
            angle = (2 * math.pi * idx) / max(1, num_vehicles)
            ox = int(depot[0] + math.cos(angle) * offset_radius)
            oy = int(depot[1] + math.sin(angle) * offset_radius)

            pygame.draw.line(screen, color, depot, (ox, oy), 2)
            pygame.draw.circle(screen, color, (ox, oy),
                               max(4, int(offset_radius / 6)))
            # Etiqueta pequena
            label = font.render(f"V{idx+1}", True, (0, 0, 0))
            label_rect = label.get_rect(midleft=(ox + 8, oy))
            screen.blit(label, label_rect)
            continue

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


def draw_legend(screen: pygame.Surface, x: int | None = None, y: int | None = None, num_vehicles: int = 0, theme: str = "auto"):
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
    right_lines = max(1, num_vehicles)
    total_lines = max(left_lines, right_lines)
    box_height = int((total_lines * line_height) + margin)
    box_width = int(min(screen_width * 0.48, 420))

    # Escolhe cores de fundo/borda/texto de acordo com o tema (ou heurística 'auto')
    # Temas suportados: 'auto', 'light', 'dark'
    bg_color = (250, 250, 250, 220)
    border_color = (160, 160, 160)
    text_color = (0, 0, 0)

    if theme == "auto":
        try:
            top_left = screen.get_at((0, 0))
            avg = (top_left.r + top_left.g + top_left.b) / 3
            theme = "light" if avg > 180 else "dark"
        except Exception:
            theme = "light"

    if theme == "dark":
        bg_color = (30, 30, 30, 220)
        border_color = (100, 100, 100)
        text_color = (230, 230, 230)
    elif theme == "light":
        bg_color = (250, 250, 250, 220)
        border_color = (160, 160, 160)
        text_color = (10, 10, 10)

    # Desenha retângulo de fundo semi-transparente usando Surface com alpha
    bg_rect = pygame.Rect(x - 8, y - 8, box_width, box_height)
    try:
        overlay = pygame.Surface(
            (bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        overlay.fill(bg_color)
        screen.blit(overlay, (bg_rect.x, bg_rect.y))
        pygame.draw.rect(screen, border_color, bg_rect, 1)  # borda
    except Exception:
        # fallback sólido se Surface alpha não suportado
        solid_bg = bg_color[:3] if len(bg_color) > 3 else bg_color
        pygame.draw.rect(screen, solid_bg, bg_rect)
        pygame.draw.rect(screen, border_color, bg_rect, 1)

    # Título da legenda
    title = title_font.render("Legenda", True, text_color)
    screen.blit(title, (x + 8, y - 6))

    # Coordenadas base para colunas (ajustadas para o tamanho da caixa)
    left_x = x + 8
    right_x = x + int(box_width * 0.5) + 8

    # Itens de prioridade (coluna esquerda)
    for i, (priority, label) in enumerate(items):
        pos_y = y + (i * line_height) + 8
        color = GREEN if priority is None else PRIORITY_COLORS.get(
            priority, RED)

        pygame.draw.circle(screen, color, (left_x + 8, pos_y +
                           int(line_height / 2)), int(base_font_size * 0.45))

        text = font.render(label, True, text_color)
        screen.blit(text, (left_x + 26, pos_y))

    # Cabeçalho das rotas/veículos (coluna direita)
    vehicle_header = font.render("Rotas / Veículos:", True, text_color)
    screen.blit(vehicle_header, (right_x, y + 2))

    # Desenha cada veículo com uma linha colorida e um marcador (coluna direita)
    for i in range(num_vehicles):
        pos_y = y + 18 + (i * line_height)
        color = VEHICLE_COLORS[i % len(VEHICLE_COLORS)]

        # Linha de exemplo da rota
        pygame.draw.line(screen, color, (right_x + 6, pos_y + int(line_height / 2)),
                         (right_x + 36, pos_y + int(line_height / 2)), max(2, int(base_font_size / 3)))
        # Marcador circular no início da linha
        pygame.draw.circle(screen, color, (right_x + 6, pos_y +
                           int(line_height / 2)), max(3, int(base_font_size / 2)))

        text = font.render(f"Veículo {i+1}", True, text_color)
        screen.blit(text, (right_x + 44, pos_y))
