from api import Subsplease, ScheduleEntry
from metadata import MetadataProvider
from db import AnimeDB, LocalShow
from display import display_schedule, display_latest, display_details


def update_schedule(meta: MetadataProvider, db: AnimeDB, subs: Subsplease):
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


def show_day(meta: MetadataProvider, db: AnimeDB, subs: Subsplease, day: str):
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
    res = subs.weekly_schedule()
    week = res.unwrap().schedule

    match day:
        case 'monday':
            get_day(week.monday, meta, db, subs, current)
            print("Monday")
            display_schedule(week.monday, current)
        case 'tuesday':
            get_day(week.tuesday, meta, db, subs, current)
            print("Tuesday")
            display_schedule(week.tuesday, current)
        case 'wednesday':
            get_day(week.wednesday, meta, db, subs, current)
            print("Wednesday")
            display_schedule(week.wednesday, current)
        case 'thursday':
            get_day(week.thursday, meta, db, subs, current)
            print("Thursday")
            display_schedule(week.thursday, current)
        case 'friday':
            get_day(week.friday, meta, db, subs, current)
            print("Friday")
            display_schedule(week.friday, current)
        case 'saturday':
            get_day(week.saturday, meta, db, subs, current)
            print("Saturday")
            display_schedule(week.saturday, current)
        case 'sunday':
            get_day(week.sunday, meta, db, subs, current)
            print("Sunday")
            display_schedule(week.sunday, current)


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


def view_show(meta: MetadataProvider, db: AnimeDB, title: str):
    print(f"Searching '{title}'")
    result = meta.search_show_details(title).unwrap()
    display_details(result)


class Program:
    def __init__(self, api: Subsplease,
                 meta: MetadataProvider, db: AnimeDB):
        self.subs = api
        self.anilist = meta
        self.db = db
        self.only_tracked = False
        self.current: dict[str, LocalShow] = {}

    def load_shows(self):
        airing = self.db.get_airing_shows().unwrap()
        self.current = {x.sid: x for x in airing}

    def switch_only_tracked(self, value: bool):
        self.only_tracked = value

    def today(self):
        res = self.subs.schedule()
        today_shows = res.unwrap().schedule
        for show in today_shows:
            local = self.current.get(show.page)
            if not local:
                self.db.create_entry(show.page, show.title)
            if local and not local.anilist_id:
                fetch_show(show.title, local)
        display_schedule(res.unwrap(), self.current, self.only_tracked)

    def fetch_show(self, title: str, show: LocalShow):
        print("Fetching")
        result = self.meta.search_show(title)
        if result.is_ok():
            ani_list_show = result.ok()
            show.title_english = ani_list_show.title.english
            show.title_japanese = ani_list_show.title.native
            show.anilist_id = ani_list_show.id
            self.db.update_show(show)
