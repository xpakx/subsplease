from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from utils import Program
import argparse
from datetime import datetime


def get_day(weekday: str) -> str | None:
    weekday = weekday.strip().lower()
    if not weekday:
        return None

    days = ["monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"]
    abbrs = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    if weekday[0] in ("+", "-"):
        try:
            offset = int(weekday)
            current_idx = datetime.now().weekday()
            return days[(current_idx + offset) % 7]
        except ValueError:
            return None
    if weekday.isdigit():
        day = int(weekday)-1
        return days[day % 7]
    if weekday in abbrs:
        return days[abbrs.index(weekday)]
    if weekday in days:
        return weekday


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
            "-t", "--tracked", action="store_true",
            help="Show only tracked")
    parser.add_argument(
            "-l", "--latest", action="store_true",
            help="Get latest episodes")
    parser.add_argument(
            "-u", "--update", action="store_true",
            help="Update weekly schedule")
    parser.add_argument(
            '-d', '--download', type=int,
            help="Id to download")
    parser.add_argument(
            '-q', '--quality', type=int,
            default=720, help="Quality to download")
    parser.add_argument(
            '-w', '--weekday', type=str,
            help="Day to show")
    parser.add_argument(
            '-v', '--view', type=str,
            help="Show to view")
    parser.add_argument(
            '-e', '--episodes', type=str,
            help="Show to see episodes of")

    subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands')
    parser_show = subparsers.add_parser(
            'show',
            aliases=['s'],
            help='Operate on show'
    )
    parser_show.add_argument(
            'name',
            type=str,
            help='Name of the show'
    )
    show_subparsers = parser_show.add_subparsers(
            dest='show_action'
    )
    parser_sub = show_subparsers.add_parser(
            'subscribe',
            aliases=['sub'],
            help='Subscribe'
    )
    parser_sub.add_argument(
            "-u", "--unsubscribe", action="store_true",
            help="Unsubscribe show"
    )

    day_show = subparsers.add_parser(
            'day',
            help='Operate on day'
    )
    day_show.add_argument(
            'weekday',
            type=str,
            help='Weekday'
    )

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.load_shows()
    program.switch_only_tracked(args.tracked)

    id = args.download
    if id is not None:
        program.start_download(id, str(args.quality))
        exit(0)
    if args.command in ['show', 's']:
        program.select(args.name)
        if args.show_action in ['sub', 'subscribe']:
            program.subscribe(not args.unsubscribe)
        else:
            if program.is_show_selected():
                program.view_selected_show()
            else:
                program.view_show(args.name)
        exit(0)

    if args.command == 'day':
        day = get_day(args.weekday)
        if day:
            program.show_day(day)
        exit(0)
    to_view = args.view
    if to_view is not None:
        program.view_show(to_view)
        exit(0)

    if args.latest:
        program.latest()
    elif args.weekday:
        day = get_day(args.weekday)
        if day:
            program.show_day(day)
    elif args.update:
        program.update_schedule()
    elif args.episodes:
        program.show(args.episodes)
    else:
        program.today()
