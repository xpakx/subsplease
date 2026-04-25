import msgspec
import requests
from subsplease.result import Result, Err, Ok


class BooruTag(msgspec.Struct):
    id: int
    name: str
    count: int
    type: int
    ambiguous: bool


class SakugaBooruAPI:
    def __init__(self):
        self.url = "https://www.sakugabooru.com/"

    def search_tag(self, name: str) -> Result[list[BooruTag], str]:
        response = requests.get(
                f"{self.url}tag.json", params={
                    "name": name,
                    "type": "",
                    "order": "name"
                })

        if response.status_code != 200:
            return Err(f"Sakugabooru API Error: {response.status_code}")

        print(response.text)
        try:
            data = msgspec.json.decode(
                    response.content,
                    type=list[BooruTag]
            )
            return Ok(data)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")


if __name__ == "__main__":
    meta = SakugaBooruAPI()
    print(meta.search_tag('tongari_boushi_no_atelier'))
