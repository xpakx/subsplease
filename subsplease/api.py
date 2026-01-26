import requests
import msgspec
from result import Result, Ok, Err


class ScheduleEntry(msgspec.Struct):
    title: str
    page: str
    image_url: str
    time: str
    aired: bool


class Schedule(msgspec.Struct):
    tz: str
    schedule: list[ScheduleEntry]


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
    def __init__(self):
        self.url = "https://subsplease.org/api/"

    def schedule(self, timezone: str) -> Result[Schedule, str]:
        url = f"{self.url}?f=schedule&h=true&tz={timezone}"
        response = requests.get(url)
        if response.status_code != 200:
            return Err(f'Error {response.status_code} on request')
        data = msgspec.json.decode(
                response.content,
                type=Schedule
        )
        return Ok(data)

    def latest(self, timezone: str, page: int | None = None
               ) -> Result[list[EpisodeData], str]:
        url = f"{self.url}?f=latest&tz={timezone}"
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
