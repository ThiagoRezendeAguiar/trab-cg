from abc import ABC
from dataclasses import dataclass, field
import uuid


@dataclass(kw_only=True)
class Shape(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    color: tuple = (255, 255, 255)