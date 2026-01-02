import httpx
from src.domain.models import Location
from src.application.interfaces import ILocationService

class IpGeoLocationService(ILocationService):
    def __init__(self):
        self.url = "http://ip-api.com/json"

    async def get_current_location(self) -> Location:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            response.raise_for_status()
            data = response.json()
            
            return Location(
                latitude=data['lat'],
                longitude=data['lon'],
                name=data.get('city', 'Unknown Location')
            )

class StaticLocationService(ILocationService):
    def __init__(self, latitude: float, longitude: float, name: str = "Home"):
        self.latitude = latitude
        self.longitude = longitude
        self.name = name

    async def get_current_location(self) -> Location:
        return Location(
            latitude=self.latitude,
            longitude=self.longitude,
            name=self.name
        )
