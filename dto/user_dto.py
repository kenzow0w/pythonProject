from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserDto:
    username: str
    password: str
    role: str
    created_at: datetime
