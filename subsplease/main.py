from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.torrent import TorrentAPI
from subsplease.utils import (
        Program,
        TorrentSearchService,
        ScheduleService
)
from subsplease.day import DayService
from subsplease.date import get_day
from subsplease.config import get_data_location, load_config
from subsplease.seadex import Seadex
from subsplease.subscription import SubscriptionService
from subsplease.sakugabooru import SakugaBooruAPI
from subsplease.images import ImageService
from subsplease.command import CommandDispatcher


# MAYBE: add jikan support
# MAYBE: clean up services and extract repos
# MAYBE: tracking shows that are not on subsplease
# MAYBE: clean finished shows


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
def search_show_seadex(
        program: Program, torrent: TorrentSearchService, name: str):
    result = program.meta.search_show_details(name)
    if result.is_err():
        return
    torrent.search_seadex(result.unwrap().id)


@dispatcher.command
def clean(program: Program):
    program.fix_torrents()


@dispatcher.command
def show_delete(program: Program, name: str):
    program.select(name)
    program.delete_show()


@dispatcher.command
def show_subs(subscriptions: SubscriptionService):
    subscriptions.show_subs()


@dispatcher.command
def get_all_subs(subscriptions: SubscriptionService, program: Program):
    shows = subscriptions.get_subs()
    for show in shows:
        program.select_raw(show)
        program.find_get_new_episodes()


@dispatcher.command
def get_clips(images: ImageService, program: Program, name: str):
    program.select(name)
    show = program.selection
    if not show:
        return
    images.get_clips(show)


def main():
    config = load_config()
    meta = MetadataProvider()
    db = AnimeDB(db_path=get_data_location() / 'ani.db')
    subs = Subsplease()
    torrent = TorrentAPI(config)
    program = Program(config, subs, meta, db, torrent)
    day = DayService(subs, meta, db, program)
    schedule = ScheduleService(subs, meta, db, program)
    program.load_shows()
    dispatcher.add_service('program', program)
    dispatcher.add_service('schedule', schedule)
    dispatcher.add_service('day', day)
    dispatcher.add_preprocessor('weekday', get_day)
    sea = Seadex()
    torrent = TorrentSearchService(config, sea)
    dispatcher.add_service('torrent', torrent)
    subs = SubscriptionService(program)
    dispatcher.add_service('subscriptions', subs)
    sakuga = SakugaBooruAPI()
    images = ImageService(sakuga, db)
    dispatcher.add_service('images', images)

    dispatcher.run()


if __name__ == "__main__":
    main()
