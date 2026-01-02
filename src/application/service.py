from datetime import datetime
from typing import List, Optional
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
            # Fetch location if we don't have it, or maybe we want to update it periodically?
            # For a Pi Zero W, it might be portable. Let's update it if it's None.
            if not self.current_location:
                self.current_location = await self.location_service.get_current_location()
            
            if self.current_location:
                # Fetch connections
                # We fetch 20 to have a buffer
                new_connections = await self.transport_repo.get_connections(self.current_location, limit=20)
                self._buffer = new_connections
        except Exception as e: # httpx.HTTPStatusError
            # Log error or handle it. For now, we just print to stderr or ignore to keep UI running
            # In a real app, use a logger.
            print(f"Error updating buffer: {e}")

    def get_displayable_connections(self, limit: int = 6) -> List[Connection]:
        # Use local aware time
        now = datetime.now().astimezone()
        
        # Filter out past connections
        # We assume connection.departure_time is timezone-aware
        valid_connections = [c for c in self._buffer if c.departure_time > now]
        
        # Sort by departure time
        valid_connections.sort(key=lambda x: x.departure_time)
        
        return valid_connections[:limit]

    def get_location_name(self) -> str:
        if self.current_location and self.current_location.name:
            return self.current_location.name
        return "Locating..."
