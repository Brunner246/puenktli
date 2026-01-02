# Pünktli - Retro Cyberpunk Public Transport Dashboard

A "Smart Gadget" dashboard for Raspberry Pi Zero W that displays the next public transport connections based on your current location.

## Features
- **Sliding Window Logic**: Fetches 20 connections every 60s, updates UI every 1s.
- **Retro Cyberpunk UI**: Neon colors, CLI interface using `rich`.
- **Auto-Location**: Uses IP Geolocation to find the nearest station.
- **Swiss Transport**: Uses `transport.opendata.ch`.

## Tech Stack
- Python 3.11+
- `uv` (Package Manager)
- `rich` (UI)
- `pydantic` (Data Validation)
- `httpx` (Async HTTP)

## Project Structure
- `src/domain`: Entities (Connection, Location)
- `src/application`: Logic (ConnectionService)
- `src/infrastructure`: API Clients (SwissTransport, IpGeo)
- `src/ui`: TUI implementation

## How to Run

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Run the project**:
   ```bash
   uv run src/main.py
   ```

   `uv` will automatically create the virtual environment and install dependencies defined in `pyproject.toml`.

## Raspberry Pi Setup (Headless)
1. SSH into your Pi.
2. Clone this repo.
3. Install `uv`.
4. Run `uv run src/main.py`.
5. (Optional) Add to `.bashrc` or create a systemd service to auto-start.
