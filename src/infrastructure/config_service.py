import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from src.domain.models import Location


class IConfigSource(ABC):
    """Interface for configuration sources following Dependency Inversion Principle."""
    
    @abstractmethod
    def load(self) -> Optional[Location]:
        """Load location configuration from this source."""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get human-readable name of the configuration source."""
        pass


class FileConfigSource(IConfigSource):
    """Load configuration from a JSON file."""
    
    def __init__(self, path: Path, source_name: str):
        self._path = path
        self._source_name = source_name
    
    def load(self) -> Optional[Location]:
        if not self._path.exists():
            return None
        
        try:
            data = self._read_json_file()
            return self._parse_location_data(data)
        except Exception as e:
            print(f"Error reading {self._path}: {e}")
            return None
    
    def get_source_name(self) -> str:
        return self._source_name
    
    def _read_json_file(self) -> dict:
        """Read and parse JSON file."""
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def _parse_location_data(data: dict) -> Location:
        """Parse location data from JSON dictionary."""
        return Location(
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
            name=data.get("name", "My Station")
        )


class EnvironmentConfigSource(IConfigSource):
    """Load configuration from environment variables."""
    
    ENV_LAT = "GLEIS_LAT"
    ENV_LON = "GLEIS_LON"
    ENV_NAME = "GLEIS_NAME"
    
    def load(self) -> Optional[Location]:
        lat = os.getenv(self.ENV_LAT)
        lon = os.getenv(self.ENV_LON)
        
        if not lat or not lon:
            return None
        
        try:
            return self._create_location(lat, lon)
        except ValueError as e:
            print(f"Error parsing environment variables: {e}")
            return None
    
    def get_source_name(self) -> str:
        return "environment variables"
    
    def _create_location(self, lat: str, lon: str) -> Location:
        """Create location from string coordinates."""
        name = os.getenv(self.ENV_NAME, "Unknown")
        return Location(
            latitude=float(lat),
            longitude=float(lon),
            name=name
        )


class DefaultConfigSource(IConfigSource):
    """Fallback configuration source with default location."""
    
    DEFAULT_LAT = 46.9480
    DEFAULT_LON = 7.4474
    DEFAULT_NAME = "Bern (Fallback)"
    
    def load(self) -> Optional[Location]:
        return Location(
            latitude=self.DEFAULT_LAT,
            longitude=self.DEFAULT_LON,
            name=self.DEFAULT_NAME
        )
    
    def get_source_name(self) -> str:
        return "default fallback"


class ConfigurationService:
    """
    Service to load location configuration from multiple sources.
    Uses chain of responsibility pattern to try sources in priority order.
    """
    
    def __init__(self):
        self._sources = self._initialize_sources()
    
    @staticmethod
    def _initialize_sources() -> list[IConfigSource]:
        """Initialize configuration sources in priority order."""
        return [
            FileConfigSource(Path("station.json"), "local file"),
            FileConfigSource(Path("/boot/station.json"), "boot partition"),
            EnvironmentConfigSource(),
            DefaultConfigSource()
        ]
    
    def load_location(self) -> Location:
        """Load location from the first available configuration source."""
        for source in self._sources:
            location = source.load()
            if location:
                self._log_configuration_loaded(source, location)
                return location
        
        # This should never happen since DefaultConfigSource always returns a location
        raise RuntimeError("No configuration source available")
    
    @staticmethod
    def _log_configuration_loaded(source: IConfigSource, location: Location) -> None:
        """Log which configuration source was used."""
        source_name = source.get_source_name()
        
        if isinstance(source, DefaultConfigSource):
            print(f"WARNING: No configuration found! Using fallback location (Bern).")
        else:
            print(f"Configuration loaded from {source_name}: {location.name}")
