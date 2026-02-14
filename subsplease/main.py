from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import Program
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location


def subscribe(program, name, unsubscribe):
    program.select(name)
    program.subscribe(not unsubscribe)


def show_latest(program, name):
    program.select(name)
    program.show_episodes()


def show_get(program, name, episode):
    program.select(name)
    if episode:
        program.find_and_get_episode(episode)
    # TODO: latest/all undownloaded


def show_view(program, name):
    program.select(name)
    if program.is_show_selected():
        program.view_selected_show()
    else:
        program.view_show(name)


def main():
    parser = get_parser()
    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB(db_path=get_data_location())
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.load_shows()
    # program.switch_only_tracked(args.tracked)

    if args.command in ['show', 's']:
        if args.show_action in ['sub', 'subscribe']:
            subscribe(program, args.name, args.unsubscribe)
        elif args.show_action == 'latest':
            show_latest(program, args.name)
        elif args.show_action == 'get':
            show_get(program, args.name, args.episode)
        else:
            show_view(program, args.name)

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


if __name__ == "__main__":
    main()
