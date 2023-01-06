import uuid
from dataclasses import dataclass, field
from .category import Category


@dataclass
class Product:
    name: str
    description: str
    price: float
    weight: float
    category: str
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
