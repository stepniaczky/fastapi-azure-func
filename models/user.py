import uuid
from dataclasses import dataclass, field


@dataclass
class User:
    first_name: str
    last_name: str
    email: str
    password: str
    phone_number: str
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
