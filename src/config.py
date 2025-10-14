#  ============= pygame constant values ================
from models import Priority

WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450
MARGIN = 30

#  ============= GA constant values =====================
N_CITIES = 15
POPULATION_SIZE = 100
N_GENERATIONS = 1000
TIME_LIMIT_SECONDS = 10  # 10 segundos
MUTATION_PROBABILITY = 0.5

#  ============= VRP constant values ====================
NUM_VEHICLES = 3  # Número de veículos disponíveis

# Parâmetros de entregas
MIN_DELIVERY_WEIGHT = 5.0  # Peso mínimo de uma entrega em kg
MAX_DELIVERY_WEIGHT = 25.0  # Peso máximo de uma entrega em kg

# Penalidades para função fitness
PENALTY_OVERLOAD = 1000.0  # Penalidade por exceder capacidade
PENALTY_PRIORITY = 50.0  # Penalidade base por atraso de prioridade

# Margem de capacidade extra da frota (10% a mais que o peso total)
FLEET_CAPACITY_MARGIN = 1.1

# ============= colors ===========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 187, 119)  # Cor para cidade inicial/final
GRAY = (128, 128, 128)

# Cores para prioridades
PRIORITY_COLORS = {
    Priority.CRITICAL: (255, 0, 0),  # Vermelho intenso
    Priority.HIGH: (255, 140, 0),  # Laranja
    Priority.MEDIUM: (255, 215, 0),  # Amarelo
    Priority.LOW: (100, 149, 237),  # Azul claro
}

# Cores para veículos (rotas diferentes)
VEHICLE_COLORS = [
    (0, 0, 255),  # Azul
    (6, 64, 43),  # Verde
    (148, 0, 211),  # Magenta
    (0, 255, 255),  # Ciano
    (255, 128, 0),  # Laranja
]


att_48_cities_locations = [
    (6734, 1453),
    (2233, 10),
    (5530, 1424),
    (401, 841),
    (3082, 1644),
    (7608, 4458),
    (7573, 3716),
    (7265, 1268),
    (6898, 1885),
    (1112, 2049),
    (5468, 2606),
    (5989, 2873),
    (4706, 2674),
    (4612, 2035),
    (6347, 2683),
    (6107, 669),
    (7611, 5184),
    (7462, 3590),
    (7732, 4723),
    (5900, 3561),
    (4483, 3369),
    (6101, 1110),
    (5199, 2182),
    (1633, 2809),
    (4307, 2322),
    (675, 1006),
    (7555, 4819),
    (7541, 3981),
    (3177, 756),
    (7352, 4506),
    (7545, 2801),
    (3245, 3305),
    (6426, 3173),
    (4608, 1198),
    (23, 2216),
    (7248, 3779),
    (7762, 4595),
    (7392, 2244),
    (3484, 2829),
    (6271, 2135),
    (4985, 140),
    (1916, 1569),
    (7280, 4899),
    (7509, 3239),
    (10, 2676),
    (6807, 2993),
    (5185, 3258),
    (3023, 1942),
]

att_48_cities_order = [
    1,
    8,
    38,
    31,
    44,
    18,
    7,
    28,
    6,
    37,
    19,
    27,
    17,
    43,
    30,
    36,
    46,
    33,
    20,
    47,
    21,
    32,
    39,
    48,
    5,
    42,
    24,
    10,
    45,
    35,
    4,
    26,
    2,
    29,
    34,
    41,
    16,
    22,
    3,
    23,
    14,
    25,
    13,
    11,
    12,
    15,
    40,
    9,
    1,
]
