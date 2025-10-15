from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Delivery:
    location: Tuple[int, int]
    priority: Priority
    weight: float
    id: int
