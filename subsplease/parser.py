import argparse


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument(
    # "-t", "--tracked", action="store_true",
    # help="Show only tracked")
    parser.set_defaults(cmd_key='today')

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
    parser_show.set_defaults(cmd_key='show_view')
    show_subparsers = parser_show.add_subparsers(
            dest='show_action'
    )
    parser_sub = show_subparsers.add_parser(
            'subscribe',
            aliases=['sub'],
            help='Subscribe'
    )
    parser_sub.set_defaults(cmd_key='subscribe')
    parser_sub.add_argument(
            "-u", "--unsubscribe", action="store_true",
            help="Unsubscribe show"
    )
    eps_for_show_sub = show_subparsers.add_parser(
            'latest',
            help='Latest episodes for the show'
    )
    eps_for_show_sub.set_defaults(cmd_key='show_latest')
    ep_get_sub = show_subparsers.add_parser(
            'get',
            help='get episode'
    )
    ep_get_sub.set_defaults(cmd_key='show_get')
    ep_get_sub.add_argument(
            "-e", "--episode", type=int,
            help="episode number"
    )

    day_show = subparsers.add_parser(
            'day',
            help='Operate on day'
    )
    day_show.set_defaults(cmd_key='day')
    day_show.add_argument(
            'weekday',
            type=str,
            help='Weekday'
    )

    parser_sync = subparsers.add_parser(
            'sync',
            help='Sync files'
    )
    parser_sync.set_defaults(cmd_key='sync')

    parser_season = subparsers.add_parser(
            'season',
            help='Weekly schedule'
    )
    parser_season.set_defaults(cmd_key='show_season')
    season_subparsers = parser_season.add_subparsers(
            dest='season_action'
    )
    parser_schedule_sync = season_subparsers.add_parser(
            'update',
            help='Update schedule'
    )
    parser_schedule_sync.set_defaults(cmd_key='update_season')

    parser_clean = subparsers.add_parser(
            'clean',
            help='Clean torrents'
    )
    parser_clean.set_defaults(cmd_key='clean')

    parser_latest = subparsers.add_parser(
            'latest',
            help='All latest uploads'
    )
    parser_latest.set_defaults(cmd_key='all_latest')

    parser_search = subparsers.add_parser(
            'search',
            help='Search meta data'
    )
    parser_search.add_argument(
            'name',
            type=str,
            help='Name of the show'
    )
    parser_search.set_defaults(cmd_key='search_show_meta')

    parser_delete = show_subparsers.add_parser(
            'delete',
            help='Delete show'
    )
    parser_delete.set_defaults(cmd_key='show_delete')
    return parser
