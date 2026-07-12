from subsplease.utils import Program
from subsplease.day import DayService
from subsplease.api import Week, Subsplease
from subsplease.db import AnimeDB


class SeasonService:
    def __init__(
            self, program: Program, day: DayService,
            subs: Subsplease, db: AnimeDB
    ):
        self.program = program
        self.subs = subs
        self.db = db
        self.day = day

    def update_schedule(self):
        res = self.subs.weekly_schedule().unwrap()
        self.finish_old(res.schedule)
        for day_name, day_list in res.schedule:
            print(f"Updating {day_name.title()}")
            self.day.update_local(day_list)

    def finish_old(self, week: Week):
        ids = set()
        for _, day in week:
            for show in day:
                if show.page:
                    ids.add(show.page)
        for show in self.program.current.values():
            if show.sid not in ids:
                show.current = False
                show.tracking = False
                print(show.sid, show.title_english)
                self.db.update_show(show)
