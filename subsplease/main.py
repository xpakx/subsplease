from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import Program
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location


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


if __name__ == "__main__":
    main()
