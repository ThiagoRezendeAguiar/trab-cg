from dataclasses import dataclass

from data_structures.point import Point
from data_structures.shape import Shape

@dataclass
class LineSegment(Shape):
    a: Point
    b: Point