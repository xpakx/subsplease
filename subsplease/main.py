from subsplease.api import Subsplease
from subsplease.meta.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.torrent import TorrentAPI, TorrentSearchService
from subsplease.utils import Program
from subsplease.schedule import ScheduleService
from subsplease.day import DayService
from subsplease.date import get_day
from subsplease.config import get_data_location, load_config
from subsplease.seadex import Seadex
from subsplease.subscription import SubscriptionService
from subsplease.sakugabooru import SakugaBooruAPI
from subsplease.images import ImageService
from subsplease.command import CommandDispatcher, CmdArg
from subsplease.meta.tenrai import TenraiMetadataProvider
from subsplease.season import SeasonService


# MAYBE: clean up services and extract repos
# MAYBE: tracking shows that are not on subsplease


dispatcher = CommandDispatcher()


@dispatcher.command(['show', ':name', 'subscribe'], aliases=['sub'])
@dispatcher.flag('unsubscribe', aliases=['-u'], help='Unsubscribe the show')
def subscribe(program: Program, name: str, unsubscribe: bool):
    '''Subscribe the show'''
    program.select(name)
    program.subscribe(not unsubscribe)


@dispatcher.command(['show', ':name', 'latest'])
def show_latest(program: Program, name: str):
    '''Latest episodes for the show'''
    program.select(name)
    program.show_episodes()


@dispatcher.command(['show', ':name', 'data'])
def show_data(program: Program, name: str):
    '''Explicit local data for the show'''
    program.select(name)
    selection = program.selection
    if not selection:
        return
    print(f"subsplease link: {selection.sid}")
    print(f"subsplease id: {selection.subsplease_id}")
    print(f"anilist id: {selection.anilist_id}")
    print(f"mal id: {selection.jikan_id}")
    print(f"sakugabooru tag: {selection.sakugaboru_tag}")
    print(f"title english: {selection.title_english}")
    print(f"title romaji: {selection.title_romaji}")
    print(f"title japanese: {selection.title_japanese}")
    print()
    print(f"target dir: {selection.dir_name}")
    print(f"last episode: {selection.last_episode}")
    print(f"subscribed: {selection.tracking}")
    print(f"current season: {selection.current}")


@dispatcher.command(['show', ':name', 'get'])
@dispatcher.flag('episode', aliases=['-e'], help='episode number')
def show_get(program: Program, name: str, episode: int | None):
    '''Get episode(s) of the show'''
    program.select(name)
    if episode:
        program.find_and_get_episode(episode)
    else:
        program.find_get_new_episodes()


@dispatcher.command(['show', CmdArg('name', help='Name of the show')],
                    aliases=['s'])
def show_view(program: Program, name: str):
    '''Operate on show'''
    program.select(name)
    if program.is_show_selected():
        program.view_selected_show()
    else:
        program.view_show(name)


@dispatcher.command(['day', CmdArg('weekday', help='Weekday')])
def day(day: DayService, weekday: str | None):
    '''Show schedule for day'''
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
def update_season(season: SeasonService):
    '''Update schedule'''
    season.update_schedule()


@dispatcher.command([])
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


@dispatcher.command(['search', ':name', 'mal'])
def search_show_mal(program: Program, name: str):
    '''Search metadata on my anime list'''
    program.view_show_jikan(name)


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
@dispatcher.flag('path', aliases=['-p'], help='Path to save')
def get_clips(
        images: ImageService, program: Program, name: str, path: str | None):
    '''Download clips for a given show'''
    program.select(name)
    show = program.selection
    if not show:
        return
    images.get_clips(show, path)


@dispatcher.command(['show', ':name', 'update', ':title'])
def update_metadata(program: Program, name: str, title: str):
    '''Force updating show metadata'''
    program.select(name)
    if not program.selection:
        return
    program.fetch_show(title, program.selection)


def main():
    config = load_config()
    meta = MetadataProvider()
    tenrai = TenraiMetadataProvider()
    db = AnimeDB(db_path=get_data_location() / 'ani.db')
    api = Subsplease()
    torrent = TorrentAPI(config)
    program = Program(config, api, meta, db, torrent, tenrai)
    day = DayService(api, meta, db, program)
    schedule = ScheduleService(api, meta, db, program)
    program.load_shows()
    dispatcher.add_service('program', program)
    dispatcher.add_service('schedule', schedule)
    dispatcher.add_service('day', day)
    dispatcher.add_preprocessor('weekday', get_day)
    sea = Seadex()
    torrent = TorrentSearchService(config, sea)
    dispatcher.add_service('torrent', torrent)
    season = SeasonService(program, day, api, db)
    dispatcher.add_service('season', season)
    subs = SubscriptionService(program)
    dispatcher.add_service('subscriptions', subs)
    sakuga = SakugaBooruAPI()
    images = ImageService(sakuga, db)
    dispatcher.add_service('images', images)

    dispatcher.run()


if __name__ == "__main__":
    main()
