import httpx
from datetime import datetime
from typing import List
from src.domain.models import Connection, Location
from src.application.interfaces import ITransportRepository

class SwissTransportClient(ITransportRepository):
    BASE_URL = "http://transport.opendata.ch/v1"

    async def get_connections(self, location: Location, limit: int = 20) -> List[Connection]:
        async with httpx.AsyncClient() as client:
            # 1. Find nearest station
            # transport.opendata.ch uses x for Latitude and y for Longitude
            # type=station filters to only return actual transit stations, not addresses
            # API returns stations ordered by distance (closest first)
            loc_params = {"x": location.latitude, "y": location.longitude, "type": "station"}
            loc_resp = await client.get(f"{self.BASE_URL}/locations", params=loc_params)
            loc_resp.raise_for_status()
            loc_data = loc_resp.json()
            
            stations = loc_data.get("stations", [])
            # Filter for stations with valid IDs (some results may be addresses without IDs)
            valid_stations = [s for s in stations if s.get("id")]
            
            if not valid_stations:
                print("Warning: No valid stations found near location")
                return []
            
            # Take the first valid station (closest one with an ID)
            station = valid_stations[0]
            station_id = station["id"]
            station_name = station.get("name", "Unknown")
            print(f"Using station: {station_name} (ID: {station_id})")
            
            # 2. Get Stationboard
            board_params = {"id": station_id, "limit": limit}
            board_resp = await client.get(f"{self.BASE_URL}/stationboard", params=board_params)
            board_resp.raise_for_status()
            board_data = board_resp.json()
            
            connections = []
            for entry in board_data.get("stationboard", []):
                try:
                    # Parse time
                    # entry['stop']['departure'] is ISO string e.g. "2023-10-27T14:00:00+0200"
                    dep_time_str = entry['stop']['departure']
                    if not dep_time_str:
                        continue
                        
                    dep_time = datetime.fromisoformat(dep_time_str)
                    
                    # Construct line name
                    category = entry.get('category', '')
                    number = entry.get('number', '')
                    line_name = f"{category} {number}".strip()
                    
                    # Get delay in minutes (API provides it in minutes)
                    delay = entry['stop'].get('delay')
                    
                    conn = Connection(
                        destination=entry['to'],
                        departure_time=dep_time,
                        line=line_name,
                        platform=entry['stop'].get('platform'),
                        delay=delay
                    )
                    connections.append(conn)
                except (ValueError, KeyError) as e:
                    # Skip malformed entries
                    continue
                
            return connections
