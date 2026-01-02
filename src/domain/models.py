from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None

class Connection(BaseModel):
    destination: str
    departure_time: datetime
    line: str
    platform: Optional[str] = None
    delay: Optional[int] = None  # Delay in minutes
    
    @property
    def formatted_time(self) -> str:
        return self.departure_time.strftime("%H:%M")
    
    @property
    def formatted_delay(self) -> str:
        if self.delay is None or self.delay == 0:
            return "-"
        return f"+{self.delay}"
