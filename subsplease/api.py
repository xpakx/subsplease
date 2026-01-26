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
