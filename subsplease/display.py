from api import Schedule
from rich.console import Console
from rich.table import Table
from rich import box


def display_schedule(data: Schedule):
    console = Console()
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold color(255)",
        border_style="blue",
    )

    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Title", style="white")

    for entry in data.schedule:
        if entry.aired:
            time_display = f"[dim]{entry.time}[/dim]"
            status = "[dim]✅ Aired[/dim]"
            title = f"[dim]{entry.title}[/dim]"
            row_style = "dim"
        else:
            time_display = f"[bold cyan]{entry.time}[/bold cyan]"
            status = "[bold green]⏳ Upcoming[/bold green]"
            title = f"[bold white]{entry.title}[/bold white]"
            row_style = ""

        table.add_row(time_display, status, title, style=row_style)

    console.print(table)
