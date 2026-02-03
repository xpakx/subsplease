from api import Schedule, ScheduleEntry, EpisodeData
from db import LocalShow
from metadata import AniListMediaDetails
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime


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


def display_latest(
        latest: list[EpisodeData],
        local: dict[str, LocalShow] | None = None,
        only_tracked: bool = False):
    console = Console()
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold color(255)",
        border_style="blue",
    )

    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Episode", justify="center", width=12)
    table.add_column("Title", style="white")

    for num, entry in enumerate(latest):
        title = entry.show
        new_ep = entry.time == 'New'
        if local:
            local_entry = local.get(entry.page)
            if local_entry and local_entry.title_english is not None:
                title = local_entry.title_english
            if only_tracked and (not local_entry or not local_entry.tracking):
                continue
        if new_ep:
            date = f"[bold cyan]{entry.release_date}[/bold cyan]"
            status = "[bold white] New[/bold white]"
            title = f"[bold green]{title}[/bold green]"
            episode = f"[white]\[{num}] {entry.episode}[/white]"
            row_style = "dim"
        else:
            date = f"[dim]{entry.release_date}[/dim]"
            status = ""
            title = f"[dim]{title}[/dim]"
            episode = f"[dim]{entry.episode}[/dim]"
            row_style = ""

        table.add_row(date, episode + status, title, style=row_style)

    console.print(table)


def display_details(show: AniListMediaDetails):
    console = Console()

    clean_desc = show.description or "No description."
    title = show.title.english or show.title.romaji
    status_color = "green" if show.status == "RELEASING" else "blue"
    status_info = f"[{status_color}]{show.status}[/{status_color}]"

    tag_list = [f"#{t.name}" for t in show.tags[:8]]
    tags_display = "  ".join(tag_list)

    content = Text()
    content.append(f"{clean_desc}\n\n", style="white")
    content.append(f"{tags_display}", style="dim")

    panel = Panel(
        content,
        title=f"[bold yellow]{title}[/]",
        subtitle=f"{status_info}",
        expand=False,
        border_style="bright_blue",
        padding=(1, 2)
    )

    console.print(panel)

    if show.nextAiringEpisode:
        dt = datetime.fromtimestamp(show.nextAiringEpisode.airingAt)
        day = dt.strftime('%A')
        time = dt.strftime('%H:%M')
        airing_info = f"\n[bold cyan]Next Ep {show.nextAiringEpisode.episode}:[/] {day} at {time}"
        console.print(airing_info)

    console.print("\n")
