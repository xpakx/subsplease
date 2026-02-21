from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.utils import (
        Program,
        TorrentSearchService,
        ScheduleService
)
from subsplease.day import DayService
from subsplease.parser import get_parser
from subsplease.date import get_day
from subsplease.config import get_data_location
from inspect import signature
from dataclasses import dataclass
from typing import Callable, Any
from subsplease.seadex import Seadex


# MAYBE: clean up services and extract repos
# MAYBE: add jikan support
# MAYBE: tracking shows that are not on subsplease
# MAYBE: clean finished shows
# MAYBE: images from sakugabooru/seadex
#        to check if series is worth watching


@dataclass
class CommandDefiniton:
    name: str
    arguments: list[str]
    func: Callable


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, CommandDefiniton] = {}
        self.services: dict[str, Any] = {}
        self.preprocessors: dict[str, Callable] = {}

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

    def add_preprocessor(self, name: str, processor: Callable):
        self.preprocessors[name] = processor

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
                value = vs.get(elem)
                if elem in self.preprocessors:
                    value = self.preprocessors[elem](value)
                kwargs[elem] = value
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
def day(day: DayService, weekday: str | None):
    if weekday:
        day.show_day(weekday)


@dispatcher.command
def sync(program: Program):
    program.check_downloads()


@dispatcher.command
def show_season(schedule: ScheduleService):
    schedule.show_schedule()


@dispatcher.command
def update_season(day: DayService):
    day.update_schedule()


@dispatcher.command
def today(day: DayService):
    day.today()


@dispatcher.command
def all_latest(schedule: ScheduleService):
    schedule.latest()


@dispatcher.command
def search_show_meta(program: Program, name: str):
    program.view_show(name)


@dispatcher.command
def search_show_torrents(torrent: TorrentSearchService, name: str):
    torrent.search(name)


@dispatcher.command
def clean(program: Program):
    program.fix_torrents()


@dispatcher.command
def show_delete(program: Program, name: str):
    program.select(name)
    program.delete_show()


def main():
    parser = get_parser()
    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB(db_path=get_data_location() / 'ani.db')
    subs = Subsplease()
    program = Program(subs, meta, db)
    day = DayService(subs, meta, db, program)
    schedule = ScheduleService(subs, meta, db, program)
    program.load_shows()
    dispatcher.add_service('program', program)
    dispatcher.add_service('schedule', schedule)
    dispatcher.add_service('day', day)
    dispatcher.add_preprocessor('weekday', get_day)
    # program.switch_only_tracked(args.tracked)
    sea = Seadex()
    torrent = TorrentSearchService(sea)
    dispatcher.add_service('torrent', torrent)

    cmd_key = getattr(args, 'cmd_key', None)
    if cmd_key:
        dispatcher.dispatch(args.cmd_key, args)


if __name__ == "__main__":
    main()
