import httpx
from datetime import datetime
from typing import List
from src.domain.models import Connection, Location
from src.application.interfaces import ITransportRepository

class SwissTransportClient(ITransportRepository):
    BASE_URL = "http://transport.opendata.ch/v1"

    async def get_connections(self, location: Location, limit: int = 20) -> List[Connection]:
        async with httpx.AsyncClient() as client:
            station = await self._find_nearest_station(client, location)
            if not station:
                return []
            
            stationboard_entries = await self._fetch_stationboard(client, station["id"], limit)
            connections = self._parse_stationboard_entries(stationboard_entries)
            
            return connections

    async def _find_nearest_station(self, client: httpx.AsyncClient, location: Location) -> dict | None:
        """Find the nearest valid station for the given location."""
        loc_params = {
            "x": location.latitude,
            "y": location.longitude,
            "type": "station"
        }
        
        loc_resp = await client.get(f"{self.BASE_URL}/locations", params=loc_params)
        loc_resp.raise_for_status()
        loc_data = loc_resp.json()
        
        valid_stations = self._filter_valid_stations(loc_data.get("stations", []))
        
        if not valid_stations:
            print("Warning: No valid stations found near location")
            return None
        
        station = valid_stations[0]
        station_name = station.get("name", "Unknown")
        print(f"Using station: {station_name} (ID: {station['id']})")
        
        return station

    @staticmethod
    def _filter_valid_stations(stations: list) -> list:
        """Filter stations to include only those with valid IDs."""
        return [station for station in stations if station.get("id")]

    async def _fetch_stationboard(self, client: httpx.AsyncClient, station_id: str, limit: int) -> list:
        """Fetch stationboard data for the given station."""
        board_params = {"id": station_id, "limit": limit}
        board_resp = await client.get(f"{self.BASE_URL}/stationboard", params=board_params)
        board_resp.raise_for_status()
        board_data = board_resp.json()
        
        return board_data.get("stationboard", [])

    def _parse_stationboard_entries(self, entries: list) -> List[Connection]:
        """Parse stationboard entries into Connection objects."""
        connections = []
        
        for entry in entries:
            connection = self._parse_single_entry(entry)
            if connection:
                connections.append(connection)
        
        return connections

    def _parse_single_entry(self, entry: dict) -> Connection | None:
        """Parse a single stationboard entry into a Connection object."""
        try:
            dep_time_str = entry['stop']['departure']
            if not dep_time_str:
                return None
            
            dep_time = datetime.fromisoformat(dep_time_str)
            line_name = self._build_line_name(entry)
            
            return Connection(
                destination=entry['to'],
                departure_time=dep_time,
                line=line_name,
                platform=entry['stop'].get('platform'),
                delay=entry['stop'].get('delay')
            )
        except (ValueError, KeyError):
            return None

    @staticmethod
    def _build_line_name(entry: dict) -> str:
        """Build line name from category and number."""
        category = entry.get('category', '')
        number = entry.get('number', '')
        return f"{category} {number}".strip()
