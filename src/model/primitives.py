from dataclasses import dataclass
from enum import Enum
from typing import List, NamedTuple

class PrimitiveType(Enum):
    POINT = 1
    LINE = 2
    CIRCLE = 3
    POLYGON = 4

class Point(NamedTuple):
    x: int
    y: int

@dataclass
class Primitive:
    type:  PrimitiveType
    p: List[Point]
    color: tuple = (0, 0, 0)
    algorithm: any = None
    radius: int = 0
    selected: bool = False