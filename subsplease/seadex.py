from subsplease.result import Result, Err, Ok
import requests
import msgspec
from typing import Any


class SeadexFile(msgspec.Struct):
    length: int


class SeadexEntry(msgspec.Struct):
    collectionName: str
    created: str
    dualAudio: bool
    groupedUrl: str
    infoHash: str
    isBest: bool
    tracker: str
    url: str
    updated: str
    files: list[SeadexFile]

    def length(self) -> int:
        return sum([x.length for x in self.files])

    def size(self) -> str:
        return format_bytes(self.length())


class SeadexExpand(msgspec.Struct):
    trs: list[SeadexEntry]


class SeadexItem(msgspec.Struct):
    comparison: str
    expand: SeadexExpand


class SeadexResponse(msgspec.Struct):
    totalItems: int
    items: list[SeadexItem]


class Seadex:
    def __init__(self):
        self.url = "https://releases.moe/api"
        self.session = requests.Session()

    def api_get(self, addr: str, params: dict) -> Result[bytes, str]:
        try:
            response = self.session.get(f"{self.url}{addr}", params=params)

            if response.status_code != 200:
                return Err(f'HTTP Error {response.status_code}')
            return Ok(response.content)

        except requests.RequestException as e:
            return Err(f"Network Error: {str(e)}")

    def schedule(self, id: int) -> Result[Any, str]:
        filter = f'alID="{id}"'
        response = self.api_get(
                '/collections/entries/records',
                {
                    'page': 1,
                    'perPage': 1,
                    'skipTotal': 1,
                    'expand': 'trs',
                    'filter': filter,
                }
        )
        return response.try_map(
                lambda r: msgspec.json.decode(r, type=SeadexResponse)
        )


def format_bytes(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"


if __name__ == "__main__":
    dex = Seadex()
    resp = dex.schedule(179302).unwrap()
    entries = resp.items[0].expand.trs
    for entry in entries:
        print(entry.tracker)
        print(entry.infoHash)
        print(entry.url)
        print(entry.created)
        print(entry.size())
        print()
