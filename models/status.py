import uuid
from dataclasses import dataclass, field


StatusLevel = {
    1: 'Unapproved',
    2: 'Approved',
    3: 'Cancelled',
    4: 'Delivered'
}


@dataclass
class Status:
    _id: int
    name: str
