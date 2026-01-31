from api import Schedule, ScheduleEntry
from db import LocalShow
from rich.console import Console
from rich.table import Table
from rich import box


def display_schedule(
        data: Schedule | list[ScheduleEntry],
        local: dict[str, LocalShow] | None = None,
        only_tracked: bool = False):
    if isinstance(data, Schedule):
        data = data.schedule
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

    for entry in data:
        title = entry.title
        if local:
            local_entry = local.get(entry.page)
            if local_entry and local_entry.title_english is not None:
                title = local_entry.title_english
            if only_tracked and (not local_entry or not local_entry.tracking):
                continue
        if entry.aired:
            time_display = f"[dim]{entry.time}[/dim]"
            status = "[dim]✅ Aired[/dim]"
            title = f"[dim]{title}[/dim]"
            row_style = "dim"
        else:
            time_display = f"[bold cyan]{entry.time}[/bold cyan]"
            status = "[bold green]⏳ Upcoming[/bold green]"
            title = f"[bold white]{title}[/bold white]"
            row_style = ""

        table.add_row(time_display, status, title, style=row_style)

    console.print(table)
