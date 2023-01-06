import uuid
from typing import Dict
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Order:
    status: str
    email: str
    phone_number: str
    ordered_products: Dict[str, int]
    _id: str = field(default_factory=lambda: str(uuid.uuid4()))
    approval_date: str or None = None

    def __post_init__(self):
        if self.approval_date is None:
            self.approval_date = date.today().strftime('%d/%m/%Y')
