from subsplease.result import Result, Err, Ok
import requests
import msgspec
from typing import Any


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


if __name__ == "__main__":
    dex = Seadex()
    resp = dex.schedule(179302)
    print(resp)

