from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from utils import Program
from datetime import datetime
from parser import get_parser
import os
from pathlib import Path


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


def get_db_location() -> str:
    path_str = os.environ.get('XDG_CACHE_HOME')
    if path_str:
        path_str = Path(path_str)
    else:
        home = os.environ.get('HOME')
        path_str = Path(home) / '.cache'
    path = path_str / 'subsplease'
    print('path', path)
    return path


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB(db_path=get_db_location())
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
