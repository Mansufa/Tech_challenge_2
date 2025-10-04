# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:03:11 2023

@author: SérgioPolimante
"""
import pylab
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
import pygame
from typing import List, Tuple

matplotlib.use("Agg")


def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', y_label: str = 'Fitness') -> None:
    """
    Draw a plot on a Pygame screen using Matplotlib.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the plot on.
    - x (list): The x-axis values.
    - y (list): The y-axis values.
    - x_label (str): Label for the x-axis (default is 'Generation').
    - y_label (str): Label for the y-axis (default is 'Fitness').
    """
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.plot(x, y)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    # Try a few fallback methods to get raw image bytes from the canvas since
    # different Matplotlib versions expose different APIs.
    width, height = canvas.get_width_height()

    raw_data = None
    # Preferred: canvas.tostring_rgb() -> returns RGB bytes
    if hasattr(canvas, "tostring_rgb"):
        try:
            raw_data = canvas.tostring_rgb()
        except Exception:
            raw_data = None

    # Fallback: buffer_rgba() or tostring_argb()
    if raw_data is None:
        if hasattr(canvas, "buffer_rgba"):
            buf = canvas.buffer_rgba()
            # buffer_rgba may return a memoryview-like object
            arr = np.frombuffer(buf, dtype=np.uint8)
            try:
                arr = arr.reshape((height, width, 4))
            except Exception:
                # reshape failed -> try transposed shape
                arr = arr.reshape((width, height, 4)).transpose((1, 0, 2))
            # Drop alpha channel (RGBA -> RGB)
            arr = arr[:, :, :3]
            raw_data = arr.tobytes()
        elif hasattr(canvas, "tostring_argb"):
            argb = canvas.tostring_argb()
            arr = np.frombuffer(argb, dtype=np.uint8)
            try:
                arr = arr.reshape((height, width, 4))
            except Exception:
                arr = arr.reshape((width, height, 4)).transpose((1, 0, 2))
            # Convert ARGB -> RGB by taking R,G,B channels (skip A)
            arr = arr[:, :, 1:4]
            raw_data = arr.tobytes()

    if raw_data is None:
        raise RuntimeError(
            "Could not extract RGB image data from Matplotlib canvas")

    size = (width, height)
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0, 0))


def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], node_radius: int) -> None:
    """
    Draws circles representing cities on the given Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface on which to draw the cities.
    - cities_locations (List[Tuple[int, int]]): List of (x, y) coordinates representing the locations of cities.
    - rgb_color (Tuple[int, int, int]): Tuple of three integers (R, G, B) representing the color of the city circles.
    - node_radius (int): The radius of the city circles.

    Returns:
    None
    """
    for city_location in cities_locations:
        pygame.draw.circle(screen, rgb_color, city_location, node_radius)


def draw_paths(screen: pygame.Surface, path: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], width: int = 1):
    """
    Draw a path on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the path on.
    - path (List[Tuple[int, int]]): List of tuples representing the coordinates of the path.
    - rgb_color (Tuple[int, int, int]): RGB values for the color of the path.
    - width (int): Width of the path lines (default is 1).
    """
    pygame.draw.lines(screen, rgb_color, True, path, width=width)


def draw_text(screen: pygame.Surface, text: str, color: pygame.Color, position: tuple | None = None) -> None:
    """
    Draw text on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the text on.
    - text (str): The text to be displayed.
    - color (pygame.Color): The color of the text.
    """
    pygame.font.init()  # You have to call this at the start

    font_size = 15
    my_font = pygame.font.SysFont('Arial', font_size)
    text_surface = my_font.render(text, False, color)

    # If no position provided, draw at bottom-left with a small margin
    if position is None:
        screen_w, screen_h = screen.get_size()
        text_position = (10, int(screen_h - 1.5 * font_size))
    else:
        text_position = position

    screen.blit(text_surface, text_position)
