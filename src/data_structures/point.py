from dataclasses import dataclass

from data_structures.shape import Shape


@dataclass
class Point(Shape):
    x: float
    y: float
    