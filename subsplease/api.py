import requests
import msgspec


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

    def schedule(self, timezone: str):
        url = f"{self.url}?f=schedule&h=true&tz={timezone}"
        response = requests.get(url)
        return msgspec.json.decode(
                response.content,
                type=Schedule
        )
