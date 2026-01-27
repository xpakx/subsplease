import requests
import msgspec
from result import Result, Ok, Err


class ScheduleEntry(msgspec.Struct):
    title: str
    page: str
    image_url: str
    time: str
    aired: bool | None = None


class Schedule(msgspec.Struct):
    tz: str
    schedule: list[ScheduleEntry]


class Week(msgspec.Struct, rename='pascal'):
    monday: list[ScheduleEntry]
    tuesday: list[ScheduleEntry]
    wednesday: list[ScheduleEntry]
    thursday: list[ScheduleEntry]
    friday: list[ScheduleEntry]
    saturday: list[ScheduleEntry]
    sunday: list[ScheduleEntry]


class WeeklySchedule(msgspec.Struct):
    tz: str
    schedule: Week


class DownloadData(msgspec.Struct):
    res: str
    magnet: str


class EpisodeData(msgspec.Struct):
    time: str
    release_date: str
    show: str
    episode: str
    page: str
    image_url: str
    downloads: list[DownloadData]


class Subsplease:
    def __init__(self, timezone: str = 'Europe/Warsaw'):
        self.url = "https://subsplease.org/api/"
        self.timezone = timezone

    def schedule(self) -> Result[Schedule, str]:
        url = f"{self.url}?f=schedule&h=true&tz={self.timezone}"
        response = requests.get(url)
        if response.status_code != 200:
            return Err(f'Error {response.status_code} on request')
        data = msgspec.json.decode(
                response.content,
                type=Schedule
        )
        return Ok(data)

    def weekly_schedule(self) -> Result[WeeklySchedule, str]:
        url = f"{self.url}?f=schedule&tz={self.timezone}"
        response = requests.get(url)
        if response.status_code != 200:
            return Err(f'Error {response.status_code} on request')
        data = msgspec.json.decode(
                response.content,
                type=WeeklySchedule
        )
        return Ok(data)

    def latest(self, page: int | None = None
               ) -> Result[list[EpisodeData], str]:
        url = f"{self.url}?f=latest&tz={self.timezone}"
        if page is not None:
            url += f'&p={page}'
        response = requests.get(url)
        if response.status_code != 200:
            return Err(f'Error {response.status_code} on request')
        data = msgspec.json.decode(
                response.content,
                type=dict[str, EpisodeData]
        )
        return Ok(list(data.values()))
