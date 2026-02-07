import requests
import msgspec
from result import Result, Ok, Err
from selectolax.parser import HTMLParser


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
    downloads: list[DownloadData]
    image_url: str = ""
    page: str = ""


class ShowData(msgspec.Struct):
    episode: dict[str, EpisodeData]


class Subsplease:
    def __init__(self, timezone: str = 'Europe/Warsaw'):
        self.url = "https://subsplease.org/api/"
        self.scrap_url = "https://subsplease.org/shows/"
        self.timezone = timezone
        self.session = requests.Session()

    def api_get(self, params: dict) -> Result[bytes, str]:
        try:
            params['tz'] = self.timezone
            response = self.session.get(self.url, params=params)

            if response.status_code != 200:
                return Err(f'HTTP Error {response.status_code}')
            return Ok(response.content)

        except requests.RequestException as e:
            return Err(f"Network Error: {str(e)}")

    def schedule(self) -> Result[Schedule, str]:
        response = self.api_get({'f': 'schedule', 'h': 'true'})
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=Schedule)
        )

    def weekly_schedule(self) -> Result[WeeklySchedule, str]:
        response = self.api_get({'f': 'schedule'})
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=WeeklySchedule)
        )

    def latest(self, page: int | None = None
               ) -> Result[list[EpisodeData], str]:
        params = {'f': 'latest'}
        if page is not None:
            params['p'] = page
        response = self.api_get(params)
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=dict[str, EpisodeData])
        ).map(lambda r: list(r.values()))

    def show(self, show_id: int) -> Result[ShowData, str]:
        response = self.api_get({'f': 'show', 'sid': show_id})
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=ShowData)
        )

    def search(self, query: str
               ) -> Result[list[EpisodeData], str]:
        response = self.api_get({'f': 'search', 's': query})
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=dict[str, EpisodeData])
        ).map(lambda r: list(r.values()))

    def get_sid(self, page: str) -> Result[int, str]:
        try:
            url = f"{self.scrap_url}{page}"
            response = self.session.get(url)

            if response.status_code != 200:
                return Err(f"HTTP Error: {response.status_code}")

            tree = HTMLParser(response.text)
            table = tree.css_first("table[id=show-release-table]")

            if not table:
                return Err("Table 'show-release-table' not found")

            sid_value = table.attributes.get("sid", "")
            if sid_value and sid_value.isdigit():
                return Ok(int(sid_value))

            return Err("Parameter 'sid' not found in table links")

        except Exception as e:
            return Err(str(e))
