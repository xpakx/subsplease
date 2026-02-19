from subsplease.result import Result, Err, Ok
import requests
from typing import Any


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
        return response


if __name__ == "__main__":
    dex = Seadex()
    resp = dex.schedule(179302)
    print(resp)

