from subsplease.api import Subsplease
from subsplease.meta.metadata import MetadataProvider
from subsplease.db import AnimeDB
from subsplease.display import (
        display_schedule,
        display_latest,
)
from subsplease.utils import Program


class ScheduleService:
    def __init__(self, api: Subsplease,
                 meta: MetadataProvider, db: AnimeDB,
                 program: Program):
        self.subs = api
        self.meta = meta
        self.db = db
        self.program = program

    def latest(self):
        episodes = self.subs.latest()
        if episodes.is_err():
            return
        display_latest(
                episodes.unwrap(),
                self.program.current,
                self.program.only_tracked
        )

    def show_schedule(self):
        res = self.subs.weekly_schedule()
        if res.is_err():
            return
        weekly_schedule = res.unwrap()
        for day_name, day_list in weekly_schedule.schedule:
            print(day_name)
            display_schedule(day_list, self.program.current)
