import asyncio
from datetime import datetime
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich import box
from src.application.service import ConnectionService

def create_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="info", size=3),
        Layout(name="main", ratio=1)
    )
    return layout

def generate_table(connections):
    table = Table(expand=True, border_style="bright_green", header_style="bold magenta", box=box.HEAVY_EDGE)
    table.add_column("LINE", style="cyan", width=10)
    table.add_column("DESTINATION", style="bright_yellow", ratio=1)
    table.add_column("DEPARTURE", style="bold white", width=10)
    table.add_column("DELAY", style="red", width=8)
    table.add_column("PLATFORM", style="dim white", width=8)
    
    for c in connections:
        # Color delay red if there's a delay, dim if no delay
        delay_style = "red" if c.delay and c.delay > 0 else "dim white"
        table.add_row(
            c.line,
            c.destination,
            c.formatted_time,
            f"[{delay_style}]{c.formatted_delay}[/{delay_style}]",
            c.platform or "-"
        )
    return table

def update_layout(layout: Layout, service: ConnectionService):
    # Header
    layout["header"].update(
        Panel(Align.center(Text("PÜNKTLI - NEON TRANSPORT", style="bold magenta")), border_style="bright_green", box=box.HEAVY_EDGE)
    )
    
    # Info
    now_str = datetime.now().strftime("%H:%M:%S")
    loc_name = service.get_location_name()
    
    # Use markup for colors
    info_text = f"[bold cyan]{now_str}[/bold cyan]  ::  [bright_yellow]{loc_name}[/bright_yellow]"
    
    layout["info"].update(
        Panel(Align.center(info_text), border_style="bright_green", box=box.HEAVY_EDGE)
    )
    
    # Main
    connections = service.get_displayable_connections(limit=10)
    if not connections:
        content = Align.center("[dim]Scanning for connections...[/dim]")
    else:
        content = generate_table(connections)
        
    layout["main"].update(
        Panel(content, title="[bold green]DEPARTURES[/bold green]", border_style="bright_green", box=box.HEAVY_EDGE)
    )

async def background_updater(service: ConnectionService):
    """Fetches new data every 60 seconds."""
    while True:
        await service.update_buffer()
        await asyncio.sleep(60)

async def run_tui(service: ConnectionService):
    layout = create_layout()
    
    # Fetch initial data before starting the UI
    await service.update_buffer()
    
    # Start the background updater
    updater_task = asyncio.create_task(background_updater(service))
    
    # Initial update to show something immediately
    update_layout(layout, service)
    
    # Run the UI loop
    # We use auto_refresh=False and manually refresh to control the loop and allow asyncio to run
    try:
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                update_layout(layout, service)
                live.refresh()
                await asyncio.sleep(1) # Update UI every 1 second
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Clean shutdown
        updater_task.cancel()
        try:
            await updater_task
        except asyncio.CancelledError:
            pass
        raise
