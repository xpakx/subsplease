import msgspec
import requests
from subsplease.result import Result, Err, Ok


class JikanMedia(msgspec.Struct):
    id: int = msgspec.field(name="mal_id")
    title: str


class JikanMediaDetails(msgspec.Struct):
    id: int = msgspec.field(name="mal_id")
    title: str
    title_english: str
    title_japanese: str
    details: str = msgspec.field(name="synopsis")
    status: str


class MetadataProvider:
    def __init__(self):
        self.url = "https://api.jikan.moe/v4/"

    def search_show(self, query: str) -> Result[JikanMedia, str]:
        response = requests.get(
                f"{self.url}anime", params={"q": query, "limit": 1})

        if response.status_code != 200:
            return Err(f"Jikan API Error: {response.status_code}")

        try:
            raw = response.json()
            if not raw["data"]:
                return Err("No results found")

            media = msgspec.convert(raw["data"], list[JikanMedia])[0]
            return Ok(media)
        except Exception as e:
            return Err(f"Decode error: {e}")

    def fetch_titles(
            self, titles: list[str]) -> Result[dict[int, JikanMedia], str]:
        results = {}
        for title in titles:
            res = self.search_show(title)
            if res.is_ok():
                media = res.unwrap()
                results[media.mal_id] = media
        return Ok(results)

    def search_show_details(
            self, query: str) -> Result[JikanMediaDetails, str]:
        res = self.search_show(query)
        if res.is_err():
            return Err(res.err())  # type: ignore

        mal_id = res.unwrap().mal_id
        return self.search_show_details_by_id(mal_id)

    def search_show_details_by_id(
            self, id: int) -> Result[JikanMediaDetails, str]:
        response = requests.get(f"{self.url}anime/{id}/full")
        if response.status_code != 200:
            return Err(f"Jikan API Error: {response.status_code}")

        try:
            raw = response.json()
            details = msgspec.convert(raw["data"], JikanMediaDetails)
            return Ok(details)
        except Exception as e:
            return Err(f"Decode error: {e}")
