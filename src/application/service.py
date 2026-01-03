from datetime import datetime
from typing import List, Optional

import httpx

from src.domain.models import Connection, Location
from src.application.interfaces import ITransportRepository, ILocationService


class ConnectionService:
    def __init__(self, transport_repo: ITransportRepository, location_service: ILocationService):
        self.transport_repo = transport_repo
        self.location_service = location_service
        self._buffer: List[Connection] = []
        self.current_location: Optional[Location] = None

    async def update_buffer(self):
        try:
            if not self.current_location:
                self.current_location = await self.location_service.get_current_location()

            if self.current_location:
                # Fetch connections
                # We fetch 20 to have a buffer
                new_connections = await self.transport_repo.get_connections(self.current_location, limit=20)
                self._buffer = new_connections
        except httpx.HTTPStatusError as e:
            print(f"Error updating buffer: {e}")
        except Exception as e:
            print(f"Unexpected error updating buffer: {e}")

    def get_displayable_connections(self, limit: int = 6) -> List[Connection]:
        now = datetime.now().astimezone()

        valid_connections = [c for c in self._buffer if c.departure_time > now]

        valid_connections.sort(key=lambda x: x.departure_time)

        return valid_connections[:limit]

    def get_location_name(self) -> str:
        if self.current_location and self.current_location.name:
            return self.current_location.name
        return "Locating..."
