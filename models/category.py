import uuid
from dataclasses import dataclass, field


@dataclass
class Category:
    name: str
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
