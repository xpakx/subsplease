from subsplease.api import Subsplease
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.torrent import TorrentAPI
from subsplease.utils import Program, TorrentSearchService
from subsplease.schedule import ScheduleService
from subsplease.day import DayService
from subsplease.date import get_day
from subsplease.config import get_data_location, load_config
from subsplease.seadex import Seadex
from subsplease.subscription import SubscriptionService
from subsplease.sakugabooru import SakugaBooruAPI
from subsplease.images import ImageService
from subsplease.command import CommandDispatcher, CmdArg


# MAYBE: add jikan support
# MAYBE: clean up services and extract repos
# MAYBE: tracking shows that are not on subsplease
# MAYBE: clean finished shows


dispatcher = CommandDispatcher()


# TODO: subscribe should be aliased as sub
@dispatcher.command(['show', ':name', 'subscribe'])
@dispatcher.flag('unsubscribe', aliases=['-s'], help='Unsubscribe the show')
def subscribe(program: Program, name: str, unsubscribe: bool):
    program.select(name)
    program.subscribe(not unsubscribe)


@dispatcher.command(['show', ':name', 'latest'])
def show_latest(program: Program, name: str):
    """Latest episodes for the show"""
    program.select(name)
    program.show_episodes()


@dispatcher.command(['show', ':name', 'get'])
@dispatcher.flag('episode', aliases=['-e'], help='episode number')
def show_get(program: Program, name: str, episode: int):
    """Get episode(s) of the show"""
    program.select(name)
    if episode:
        program.find_and_get_episode(episode)
    else:
        program.find_get_new_episodes()


# TODO: show should be aliased as s
@dispatcher.command(['show', CmdArg('name', help='Name of the show')])
def show_view(program: Program, name: str):
    '''Operate on show'''
    program.select(name)
    if program.is_show_selected():
        program.view_selected_show()
    else:
        program.view_show(name)


@dispatcher.command(['day', CmdArg('weekday', help='Weekday', true_type=str)])
def day(day: DayService, weekday: str | None):
    if weekday:
        day.show_day(weekday)


@dispatcher.command
def sync(program: Program):
    '''Sync files'''
    program.check_downloads()


@dispatcher.command(name='season')
def show_season(schedule: ScheduleService):
    '''Weekly schedule'''
    schedule.show_schedule()


@dispatcher.command(['season', 'update'])
def update_season(day: DayService):
    '''Update schedule'''
    day.update_schedule()


@dispatcher.command
def today(day: DayService):
    day.today()


@dispatcher.command(name='latest')
def all_latest(schedule: ScheduleService):
    '''All latest uploads'''
    schedule.latest()


@dispatcher.command(['search', CmdArg('name', help='Name of the show')])
def search_show_meta(program: Program, name: str):
    '''Search metadata'''
    program.view_show(name)


@dispatcher.command(['search', ':name', 'nyaa'])
def search_show_torrents(torrent: TorrentSearchService, name: str):
    '''Search torrents'''
    torrent.search(name)


@dispatcher.command(['search', ':name', 'seadex'])
def search_show_seadex(
        program: Program, torrent: TorrentSearchService, name: str):
    '''Search seadex'''
    torrent.search(name)
    result = program.meta.search_show_details(name)
    if result.is_err():
        return
    torrent.search_seadex(result.unwrap().id)


@dispatcher.command
def clean(program: Program):
    '''Clean torrents'''
    program.fix_torrents()


@dispatcher.command(['show', ':name', 'delete'])
def show_delete(program: Program, name: str):
    '''Delete show'''
    program.select(name)
    program.delete_show()


@dispatcher.command(name='subs')
def show_subs(subscriptions: SubscriptionService):
    '''Show subscribed shows'''
    subscriptions.show_subs()


@dispatcher.command(['subs', 'get'])
def get_all_subs(subscriptions: SubscriptionService, program: Program):
    '''Get all new episodes of subscribed shows'''
    shows = subscriptions.get_subs()
    for show in shows:
        program.select_raw(show)
        program.find_get_new_episodes()


@dispatcher.command(['show', ':name', 'clips'])
def get_clips(images: ImageService, program: Program, name: str):
    '''Download clips for a given show'''
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
