from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import Program
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location
from inspect import signature


class CommandDispatcher:
    def __init__(self):
        self.commands = {}

    def register(self, name, command):
        self.commands[name] = command

    def dispatch(self, name, service, args):
        cmd = self.commands.get(name)
        if not cmd:
            return
        sig = signature(cmd)
        sig = list(sig.parameters.keys())
        # TODO: for now, we assume first one is service
        kwargs = {}
        vs = vars(args)
        for elem in sig[1:]:
            kwargs[elem] = vs.get(elem)
        if cmd:
            cmd(service, **kwargs)


dispatcher = CommandDispatcher()


def command(f):
    dispatcher.register(f.__name__, f)
    return f


@command
def subscribe(program: Program, name: str, unsubscribe: bool):
    program.select(name)
    program.subscribe(not unsubscribe)


@command
def show_latest(program: Program, name: str):
    program.select(name)
    program.show_episodes()


@command
def show_get(program: Program, name: str, episode: int):
    program.select(name)
    if episode:
        program.find_and_get_episode(episode)
    # TODO: latest/all undownloaded


@command
def show_view(program: Program, name: str):
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

    cmd_key = getattr(args, 'cmd_key', None)
    if cmd_key:
        dispatcher.dispatch(args.cmd_key, program, args)

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
