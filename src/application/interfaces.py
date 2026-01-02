from abc import ABC, abstractmethod
from typing import List
from src.domain.models import Connection, Location

class ITransportRepository(ABC):
    @abstractmethod
    async def get_connections(self, location: Location, limit: int = 20) -> List[Connection]:
        pass

class ILocationService(ABC):
    @abstractmethod
    async def get_current_location(self) -> Location:
        pass
