import json
import os
from pathlib import Path
from typing import Optional
from src.domain.models import Location

class ConfigurationService:
    """
    Service to load location configuration from multiple sources:
    1. Local station.json file (for development)
    2. Boot partition /boot/station.json (for Raspberry Pi)
    3. Environment variables (fallback)
    4. Default fallback location
    """
    
    # Local config path for development
    LOCAL_CONFIG_PATH = Path("station.json")
    
    # Boot partition path (on Raspberry Pi: /boot or /boot/firmware)
    BOOT_CONFIG_PATH = Path("/boot/station.json")
    
    def load_location(self) -> Location:
        # 1. Try local station.json (for development)
        file_location = self._load_from_file(self.LOCAL_CONFIG_PATH)
        if file_location:
            print(f"Configuration loaded from local file: {file_location.name}")
            return file_location
        
        # 2. Try boot partition (for Raspberry Pi)
        file_location = self._load_from_file(self.BOOT_CONFIG_PATH)
        if file_location:
            print(f"Configuration loaded from boot partition: {file_location.name}")
            return file_location
        
        # 3. Try environment variables
        env_location = self._load_from_environment()
        if env_location:
            print("Configuration loaded from environment variables.")
            return env_location
        
        # 4. Fallback to default location
        print("WARNING: No configuration found! Using fallback location (Bern).")
        return Location(latitude=46.9480, longitude=7.4474, name="Bern (Fallback)")
    
    def _load_from_file(self, path: Path) -> Optional[Location]:
        """Load location from a JSON file"""
        if not path.exists():
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Location(
                    latitude=float(data["lat"]),
                    longitude=float(data["lon"]),
                    name=data.get("name", "My Station")
                )
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return None
    
    def _load_from_environment(self) -> Optional[Location]:
        """Load location from environment variables"""
        lat = os.getenv("GLEIS_LAT")
        lon = os.getenv("GLEIS_LON")
        name = os.getenv("GLEIS_NAME", "Unknown")
        
        if lat and lon:
            try:
                return Location(
                    latitude=float(lat),
                    longitude=float(lon),
                    name=name
                )
            except ValueError as e:
                print(f"Error parsing environment variables: {e}")
                return None
        
        return None
