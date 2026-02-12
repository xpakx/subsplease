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
    # parser.add_argument(
    # "-t", "--tracked", action="store_true",
    # help="Show only tracked")

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
    eps_for_show_sub = show_subparsers.add_parser(
            'latest',
            help='Latest episodes for the show'
    )
    ep_get_sub = show_subparsers.add_parser(
            'get',
            help='get episode'
    )
    ep_get_sub.add_argument(
            "-e", "--episode", type=int,
            help="episode number"
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

    parser_sync = subparsers.add_parser(
            'sync',
            help='Sync files'
    )

    parser_season = subparsers.add_parser(
            'season',
            help='Weekly schedule'
    )
    season_subparsers = parser_season.add_subparsers(
            dest='season_action'
    )
    parser_schedule_sync = season_subparsers.add_parser(
            'update',
            help='Update schedule'
    )

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.load_shows()
    # program.switch_only_tracked(args.tracked)

    if args.command in ['show', 's']:
        program.select(args.name)
        if args.show_action in ['sub', 'subscribe']:
            program.subscribe(not args.unsubscribe)
        elif args.show_action == 'latest':
            program.show_episodes()
        elif args.show_action == 'get':
            if args.episode:
                program.find_and_get_episode(args.episode)
            else:
                # TODO: latest/all undownloaded
                pass
        else:
            if program.is_show_selected():
                program.view_selected_show()
            else:
                program.view_show(args.name)

    elif args.command == 'sync':
        program.check_downloads()

    elif args.command == 'day':
        day = get_day(args.weekday)
        if day:
            program.show_day(day)
    elif args.command == 'season':
        if args.season_action == 'update':
            program.update_schedule()
        else:
            program.show_schedule()
    else:
        program.today()

    # to_view = args.view
    # if to_view is not None:
        # program.view_show(to_view)
        # exit(0)

    # TODO: day latest
    # if args.latest:
        # program.latest()
