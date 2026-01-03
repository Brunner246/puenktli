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


class LayoutManager:
    """Manages the Rich layout structure following SRP."""
    
    def __init__(self):
        self._layout = self._create_layout()
    
    def get_layout(self) -> Layout:
        return self._layout
    
    def _create_layout(self) -> Layout:
        """Create the main layout structure."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="info", size=3),
            Layout(name="main", ratio=1)
        )
        return layout


class StyleConfig:
    """Centralized styling configuration following DRY principle."""
    
    BORDER_STYLE = "bright_green"
    BOX_STYLE = box.HEAVY_EDGE
    
    # Header styles
    HEADER_TEXT_STYLE = "bold magenta"
    
    # Info styles
    TIME_STYLE = "bold cyan"
    LOCATION_STYLE = "bright_yellow"
    
    # Table styles
    TABLE_HEADER_STYLE = "bold magenta"
    COLUMN_LINE_STYLE = "cyan"
    COLUMN_DESTINATION_STYLE = "bright_yellow"
    COLUMN_DEPARTURE_STYLE = "bold white"
    COLUMN_DELAY_STYLE = "red"
    COLUMN_DELAY_NONE_STYLE = "dim white"
    COLUMN_PLATFORM_STYLE = "dim white"
    
    # Main panel
    PANEL_TITLE_STYLE = "bold green"
    LOADING_TEXT_STYLE = "dim"


class TableBuilder:
    """Builds connection tables following SRP."""
    
    def __init__(self, style_config: StyleConfig):
        self._style = style_config
    
    def build_table(self, connections: list) -> Table:
        """Build a Rich table from connection data."""
        table = self._create_table_structure()
        self._add_rows(table, connections)
        return table
    
    def _create_table_structure(self) -> Table:
        """Create the table with columns."""
        table = Table(
            expand=True,
            border_style=self._style.BORDER_STYLE,
            header_style=self._style.TABLE_HEADER_STYLE,
            box=self._style.BOX_STYLE
        )
        table.add_column("LINE", style=self._style.COLUMN_LINE_STYLE, width=10)
        table.add_column("DESTINATION", style=self._style.COLUMN_DESTINATION_STYLE, ratio=1)
        table.add_column("DEPARTURE", style=self._style.COLUMN_DEPARTURE_STYLE, width=10)
        table.add_column("DELAY", style=self._style.COLUMN_DELAY_STYLE, width=8)
        table.add_column("PLATFORM", style=self._style.COLUMN_PLATFORM_STYLE, width=8)
        return table
    
    def _add_rows(self, table: Table, connections: list) -> None:
        """Add connection rows to the table."""
        for connection in connections:
            table.add_row(*self._format_connection_row(connection))
    
    def _format_connection_row(self, connection) -> tuple:
        """Format a single connection as a table row."""
        delay_style = self._get_delay_style(connection.delay)
        formatted_delay = self._format_delay_text(connection.formatted_delay, delay_style)
        
        return (
            connection.line,
            connection.destination,
            connection.formatted_time,
            formatted_delay,
            connection.platform or "-"
        )
    
    def _get_delay_style(self, delay: int | None) -> str:
        """Determine the style for delay based on its value."""
        if delay and delay > 0:
            return self._style.COLUMN_DELAY_STYLE
        return self._style.COLUMN_DELAY_NONE_STYLE
    
    @staticmethod
    def _format_delay_text(delay_text: str, style: str) -> str:
        """Format delay text with style tags."""
        return f"[{style}]{delay_text}[/{style}]"


class HeaderRenderer:
    """Renders the header section following SRP."""
    
    def __init__(self, style_config: StyleConfig):
        self._style = style_config
    
    def render(self) -> Panel:
        """Render the header panel."""
        text = Text("PÜNKTLI - NEON TRANSPORT", style=self._style.HEADER_TEXT_STYLE)
        return Panel(
            Align.center(text),
            border_style=self._style.BORDER_STYLE,
            box=self._style.BOX_STYLE
        )


class InfoRenderer:
    """Renders the info section following SRP."""
    
    def __init__(self, style_config: StyleConfig):
        self._style = style_config
    
    def render(self, location_name: str) -> Panel:
        """Render the info panel with current time and location."""
        current_time = self._get_current_time()
        info_text = self._format_info_text(current_time, location_name)
        
        return Panel(
            Align.center(info_text),
            border_style=self._style.BORDER_STYLE,
            box=self._style.BOX_STYLE
        )
    
    @staticmethod
    def _get_current_time() -> str:
        """Get current time formatted as HH:MM:SS."""
        return datetime.now().strftime("%H:%M:%S")
    
    def _format_info_text(self, time: str, location: str) -> str:
        """Format the info text with styles."""
        return (
            f"[{self._style.TIME_STYLE}]{time}[/{self._style.TIME_STYLE}]"
            f"  ::  "
            f"[{self._style.LOCATION_STYLE}]{location}[/{self._style.LOCATION_STYLE}]"
        )


class MainPanelRenderer:
    """Renders the main content section following SRP."""
    
    def __init__(self, style_config: StyleConfig, table_builder: TableBuilder):
        self._style = style_config
        self._table_builder = table_builder
    
    def render(self, connections: list) -> Panel:
        """Render the main panel with connections table."""
        content = self._get_content(connections)
        
        return Panel(
            content,
            title=f"[{self._style.PANEL_TITLE_STYLE}]DEPARTURES[/{self._style.PANEL_TITLE_STYLE}]",
            border_style=self._style.BORDER_STYLE,
            box=self._style.BOX_STYLE
        )
    
    def _get_content(self, connections: list):
        """Get panel content based on connection availability."""
        if not connections:
            return Align.center(f"[{self._style.LOADING_TEXT_STYLE}]Scanning for connections...[/{self._style.LOADING_TEXT_STYLE}]")
        return self._table_builder.build_table(connections)


class DisplayUpdater:
    """Updates the display layout following SRP."""
    
    def __init__(
        self,
        header_renderer: HeaderRenderer,
        info_renderer: InfoRenderer,
        main_panel_renderer: MainPanelRenderer
    ):
        self._header_renderer = header_renderer
        self._info_renderer = info_renderer
        self._main_panel_renderer = main_panel_renderer
    
    def update(self, layout: Layout, service: ConnectionService) -> None:
        """Update all layout sections."""
        layout["header"].update(self._header_renderer.render())
        layout["info"].update(self._info_renderer.render(service.get_location_name()))
        layout["main"].update(self._render_main_panel(service))
    
    def _render_main_panel(self, service: ConnectionService) -> Panel:
        """Render the main panel with connections."""
        connections = service.get_displayable_connections(limit=10)
        return self._main_panel_renderer.render(connections)


class BackgroundUpdater:
    """Manages background data updates following SRP."""
    
    def __init__(self, service: ConnectionService, update_interval: int = 60):
        self._service = service
        self._update_interval = update_interval
        self._task = None
    
    async def start(self) -> None:
        """Start the background update task."""
        self._task = asyncio.create_task(self._update_loop())
    
    async def stop(self) -> None:
        """Stop the background update task."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _update_loop(self) -> None:
        """Continuously fetch new data at regular intervals."""
        while True:
            await self._service.update_buffer()
            await asyncio.sleep(self._update_interval)


class TUIApplication:
    """Main TUI application following SRP and managing dependencies."""
    
    def __init__(self, service: ConnectionService):
        self._service = service
        self._style = StyleConfig()
        self._layout_manager = LayoutManager()
        self._background_updater = BackgroundUpdater(service)
        self._display_updater = self._create_display_updater()
    
    def _create_display_updater(self) -> DisplayUpdater:
        """Create display updater with all dependencies."""
        table_builder = TableBuilder(self._style)
        header_renderer = HeaderRenderer(self._style)
        info_renderer = InfoRenderer(self._style)
        main_panel_renderer = MainPanelRenderer(self._style, table_builder)
        
        return DisplayUpdater(header_renderer, info_renderer, main_panel_renderer)
    
    async def run(self) -> None:
        """Run the TUI application."""
        await self._initialize()
        await self._run_display_loop()
    
    async def _initialize(self) -> None:
        """Initialize the application with initial data."""
        await self._service.update_buffer()
        await self._background_updater.start()
    
    async def _run_display_loop(self) -> None:
        """Run the main display loop."""
        layout = self._layout_manager.get_layout()
        self._display_updater.update(layout, self._service)
        
        try:
            with self._create_live_display(layout) as live:
                await self._refresh_loop(live, layout)
        except (KeyboardInterrupt, asyncio.CancelledError):
            await self._shutdown()
            raise
    
    @staticmethod
    def _create_live_display(layout: Layout) -> Live:
        """Create the Live display context."""
        return Live(layout, refresh_per_second=4, screen=True)
    
    async def _refresh_loop(self, live: Live, layout: Layout) -> None:
        """Continuously refresh the display."""
        while True:
            self._display_updater.update(layout, self._service)
            live.refresh()
            await asyncio.sleep(1)
    
    async def _shutdown(self) -> None:
        """Clean shutdown of the application."""
        await self._background_updater.stop()


async def run_tui(service: ConnectionService):
    """Entry point for running the TUI application."""
    app = TUIApplication(service)
    await app.run()
