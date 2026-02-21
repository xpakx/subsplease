from subsplease.api import Subsplease, ScheduleEntry
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB, LocalShow
from subsplease.utils import Program
from subsplease.display import display_schedule


class DayService:
    def __init__(self, api: Subsplease,
                 meta: MetadataProvider, db: AnimeDB,
                 program: Program
                 ):
        self.subs = api
        self.meta = meta
        self.db = db
        self.program = program

    def today(self):
        res = self.subs.schedule()
        today_shows = res.unwrap().schedule
        self.update_local(today_shows)

        display_schedule(
                res.unwrap(),
                self.program.current,
                self.program.only_tracked
        )

    def update_local(self, shows: list[ScheduleEntry]):
        for show in shows:
            self.update_or_create_local_show(show)

    def update_or_create_local_show(
            self, show: ScheduleEntry
    ) -> LocalShow | None:
        local = self.program.current.get(show.page)
        if not local:
            self.db.create_entry(show.page, show.title)
        if local and not local.anilist_id:
            # TODO: repo???
            self.program.fetch_show(show.title, local)
        return local

    def show_day(self, day: str):
        res = self.subs.weekly_schedule()
        week = res.unwrap().schedule
        day_list = week.get_day(day)
        if not day_list:
            return
        self.update_local(day_list)

        print(day.capitalize())
        display_schedule(day_list, self.program.current)

    # TODO: move
    def update_schedule(self):
        res = self.subs.weekly_schedule().unwrap()
        for day_name, day_list in res.schedule:
            print(f"Updating {day_name.title()}")
            self.update_local(day_list)
