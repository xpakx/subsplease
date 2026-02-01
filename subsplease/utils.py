from api import Subsplease, ScheduleEntry
from metadata import MetadataProvider
from db import AnimeDB, LocalShow
from display import display_schedule, display_latest


def today(meta: MetadataProvider, db: AnimeDB,
          subs: Subsplease, only_tracked: bool = False):
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
    res = subs.schedule()
    today_shows = res.unwrap().schedule
    for show in today_shows:
        local = current.get(show.page)
        if not local:
            db.create_entry(show.page, show.title)
        if local and not local.anilist_id:
            fetch_show(meta, db, show.title, local)
    display_schedule(res.unwrap(), current, only_tracked)


def schedule(meta: MetadataProvider, db: AnimeDB, subs: Subsplease):
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
    res = subs.weekly_schedule()
    week = res.unwrap().schedule
    get_day(week.monday, meta, db, subs, current)
    get_day(week.tuesday, meta, db, subs, current)
    get_day(week.wednesday, meta, db, subs, current)
    get_day(week.thursday, meta, db, subs, current)
    get_day(week.friday, meta, db, subs, current)
    get_day(week.saturday, meta, db, subs, current)
    get_day(week.sunday, meta, db, subs, current)


def get_day(shows: list[ScheduleEntry], meta: MetadataProvider,
            db: AnimeDB, subs: Subsplease, current):
    for show in shows:
        local = current.get(show.page)
        if not local:
            db.create_entry(show.page, show.title)
        if local and not local.anilist_id:
            fetch_show(meta, db, show.title, local)


def fetch_show(meta: MetadataProvider, db: AnimeDB,
               title: str, show: LocalShow):
    print("Fetching")
    result = meta.search_show(title)
    if result.is_ok():
        ani_list_show = result.ok()
        show.title_english = ani_list_show.title.english
        show.title_japanese = ani_list_show.title.native
        show.anilist_id = ani_list_show.id
        db.update_show(show)


def latest(meta: MetadataProvider, db: AnimeDB,
           subs: Subsplease, only_tracked: bool = False):
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
    episodes = subs.latest()
    display_latest(episodes.unwrap(), current, only_tracked)
