from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DroneDto:
    id: Optional[int] = None
    port: Optional[str] = None
    serial_number: Optional[str] = None
    mission: Optional[str] = 'None'
    created_at: Optional[datetime] = field(default_factory=datetime.now)
