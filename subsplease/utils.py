from api import Subsplease, ScheduleEntry
from metadata import MetadataProvider
from db import AnimeDB, LocalShow
from display import display_schedule, display_latest, display_details


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

    def show_day(self, day: str):
        res = self.subs.weekly_schedule()
        week = res.unwrap().schedule
        if not hasattr(week, day):
            return
        day_list = getattr(week, day)
        self.get_day(day_list)
        print(day.capitalize())
        display_schedule(day_list, self.current)

    def get_day(self, shows: list[ScheduleEntry]):
        for show in shows:
            local = self.current.get(show.page)
            if not local:
                self.db.create_entry(show.page, show.title)
            if local and not local.anilist_id:
                self.fetch_show(show.title, local)

    def update_schedule(self):
        res = self.subs.weekly_schedule()
        week = res.unwrap().schedule
        self.get_day(week.monday)
        self.get_day(week.tuesday)
        self.get_day(week.wednesday)
        self.get_day(week.thursday)
        self.get_day(week.friday)
        self.get_day(week.saturday)
        self.get_day(week.sunday)
