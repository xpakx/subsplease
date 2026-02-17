from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import Program
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location
from inspect import signature
from dataclasses import dataclass
from typing import Callable, Any


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
                arguments=args[1:]
        )
        self.commands[name] = cmd_def

    def add_service(self, name: str, service: Any):
        self.services[name] = service

    def dispatch(self, name, service, args):
        cmd = self.commands.get(name)
        if not cmd:
            return
        kwargs = {}
        vs = vars(args)
        for elem in cmd.arguments:
            kwargs[elem] = vs.get(elem)
        cmd.func(service, **kwargs)

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
    # TODO: latest/all undownloaded


@dispatcher.command
def show_view(program: Program, name: str):
    program.select(name)
    if program.is_show_selected():
        program.view_selected_show()
    else:
        program.view_show(name)


@dispatcher.command
def day(program: Program, weekday: str):
    day = get_day(weekday)
    if day:
        program.show_day(day)


@dispatcher.command
def sync(program: Program):
    program.check_downloads()


@dispatcher.command
def show_season(program: Program):
    program.show_schedule()


@dispatcher.command
def update_season(program: Program):
    program.update_schedule()


@dispatcher.command
def today(program: Program):
    program.today()


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
    db = AnimeDB(db_path=get_data_location())
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.load_shows()
    dispatcher.add_service('program', program)
    # program.switch_only_tracked(args.tracked)

    cmd_key = getattr(args, 'cmd_key', None)
    if cmd_key:
        dispatcher.dispatch(args.cmd_key, program, args)


if __name__ == "__main__":
    main()
