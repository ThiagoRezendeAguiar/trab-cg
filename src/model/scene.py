from dataclasses import dataclass, field
from typing import List

from model.primitives import Primitive


@dataclass
class Scene:
    primitives: List[Primitive] = field(default_factory=list)

    def add_primitive(self, p: Primitive):
        self.primitives.append(p)