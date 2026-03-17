from dataclasses import dataclass, field

from data_structures.shape import Shape

@dataclass(kw_only=True)
class Scene:
    shapes: list[Shape] = field(default_factory=list)

    def add_shape(self, shape: Shape):
        self.shapes.append(shape)

    def remove_shape(self, shape_id: str):
        self.shapes = [s for s in self.shapes if s.id != shape_id]

    def clean_shapes(self):
        self.shapes.clear()