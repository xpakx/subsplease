from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import Program, DayService
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location
from inspect import signature
from dataclasses import dataclass
from typing import Callable, Any


# MAYBE: clean up services and extract repos
# MAYBE: add jikan support
# MAYBE: tracking shows no on subsplease
# MAYBE: finished shows
# MAYBE: finished shows


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefiniton] = {}
        self.services: dict[str, Any] = {}

    def register(self, name: str, command: Callable):
        sig = signature(command)
        args = list(sig.parameters.keys())
        cmd_def = CommandDefiniton(
                name=name,
                func=command,
                arguments=args
        )
        self.commands[name] = cmd_def

    def add_service(self, name: str, service: Any):
        self.services[name] = service

    def dispatch(self, name, args):
        cmd = self.commands.get(name)
        if not cmd:
            return
        kwargs = {}
        vs = vars(args)
        for elem in cmd.arguments:
            if elem in self.services:
                kwargs[elem] = self.services.get(elem)
            else:
                kwargs[elem] = vs.get(elem)
        cmd.func(**kwargs)

    def command(self, f):
        self.register(f.__name__, f)
        return f


dispatcher = CommandDispatcher()


@dispatcher.command
def subscribe(program: Program, name: str, unsubscribe: bool):
    program.select(name)
    program.subscribe(not unsubscribe)


@dispatcher.command
def show_latest(program: Program, name: str):
    program.select(name)
    program.show_episodes()


@dispatcher.command
def show_get(program: Program, name: str, episode: int):
    program.select(name)
    if episode:
        program.find_and_get_episode(episode)
    else:
        program.find_get_new_episodes()


@dispatcher.command
def show_view(program: Program, name: str):
    program.select(name)
    if program.is_show_selected():
        program.view_selected_show()
    else:
        program.view_show(name)


@dispatcher.command
def day(day: DayService, weekday: str):
    day_data = get_day(weekday)
    if day_data:
        day.show_day(day_data)


@dispatcher.command
def sync(program: Program):
    program.check_downloads()


@dispatcher.command
def show_season(program: Program):
    program.show_schedule()


@dispatcher.command
def update_season(day: DayService):
    day.update_schedule()


@dispatcher.command
def today(day: DayService):
    day.today()


# TODO
@dispatcher.command
def all_latest(program: Program):
    program.latest()


# TODO
@dispatcher.command
def search_show_meta(program: Program, name: str):
    program.view_show(name)


def main():
    parser = get_parser()
    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB(db_path=get_data_location() / 'ani.db')
    subs = Subsplease()
    program = Program(subs, meta, db)
    day = DayService(subs, meta, db, program)
    program.load_shows()
    dispatcher.add_service('program', program)
    dispatcher.add_service('day', day)
    # program.switch_only_tracked(args.tracked)

    cmd_key = getattr(args, 'cmd_key', None)
    if cmd_key:
        dispatcher.dispatch(args.cmd_key, args)


if __name__ == "__main__":
    main()
