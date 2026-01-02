import asyncio
import sys
import os

# Ensure project root is in path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.config_service import ConfigurationService
from src.infrastructure.location_service import StaticLocationService
from src.infrastructure.transport_client import SwissTransportClient
from src.application.service import ConnectionService
from src.ui.tui import run_tui

async def main():
    # Composition Root
    # Load location from configuration (station.json, environment, or fallback)
    config_service = ConfigurationService()
    location = config_service.load_location()
    
    location_service = StaticLocationService(
        latitude=location.latitude,
        longitude=location.longitude,
        name=location.name
    )

    transport_repo = SwissTransportClient()
    
    service = ConnectionService(transport_repo, location_service)
    
    try:
        await run_tui(service)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nExiting Pünktli...")
    except Exception as e:
        print(f"\nCritical Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
