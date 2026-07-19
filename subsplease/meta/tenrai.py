import msgspec
import requests
from subsplease.result import Result, Err, Ok


class TenraiMedia(msgspec.Struct):
    id: int = msgspec.field(name="mal_id")
    title: str


class TenraiTag(msgspec.Struct):
    id: int = msgspec.field(name="mal_id")
    name: str
    type: str


class TenraiMediaDetails(msgspec.Struct):
    id: int = msgspec.field(name="mal_id")
    title: str
    title_english: str
    title_japanese: str
    details: str = msgspec.field(name="synopsis")
    status: str
    genres: list[TenraiTag]
    demographics: list[TenraiTag]
    themes: list[TenraiTag]

    def tags(self) -> list[str]:
        return [
            tag.name
            for tag_group in (self.genres, self.themes, self.demographics)
            for tag in tag_group
        ]


class TenraiMetadataProvider:
    def __init__(self):
        self.url = "https://api.tenrai.org/v1/"

    def search_show(self, query: str) -> Result[TenraiMedia, str]:
        response = requests.get(
                f"{self.url}anime",
                params={
                    "q": query,
                    "limit": 1,
                },
        )

        if response.status_code != 200:
            return Err(f"Jikan API Error: {response.status_code}")

        try:
            raw = response.json()
            if not raw["data"]:
                return Err("No results found")

            media = msgspec.convert(raw["data"], list[TenraiMedia])[0]
            return Ok(media)
        except Exception as e:
            return Err(f"Decode error: {e}")

    def fetch_titles(
            self, titles: list[str]) -> Result[dict[int, TenraiMedia], str]:
        results = {}
        for title in titles:
            res = self.search_show(title)
            if res.is_ok():
                media = res.unwrap()
                results[media.id] = media
        return Ok(results)

    def search_show_details(
            self, query: str) -> Result[TenraiMediaDetails, str]:
        res = self.search_show(query)
        if res.is_err():
            return Err(res.err())  # type: ignore

        mal_id = res.unwrap().id
        return self.search_show_details_by_id(mal_id)

    def search_show_details_by_id(
            self, id: int) -> Result[TenraiMediaDetails, str]:
        response = requests.get(f"{self.url}anime/{id}/full")
        if response.status_code != 200:
            return Err(f"Jikan API Error: {response.status_code}")

        try:
            raw = response.json()
            details = msgspec.convert(raw["data"], TenraiMediaDetails)
            return Ok(details)
        except Exception as e:
            return Err(f"Decode error: {e}")

    def get_current_season_summary(self) -> Result[list[TenraiMedia], str]:
        limit = 25
        response = requests.get(
            f"{self.url}seasons/now",
            params={"limit": limit}
        )

        if response.status_code != 200:
            return Err(f"Jikan API Error: {response.status_code}")

        try:
            raw = response.json()
            if not raw.get("data"):
                return Err("No results found for current season")

            media_list = msgspec.convert(raw["data"], list[TenraiMedia])
            return Ok(media_list)
        except Exception as e:
            return Err(f"Decode error: {e}")


if __name__ == "__main__":
    meta = TenraiMetadataProvider()
    # print(meta.get_current_season_summary())
    show = meta.search_show_details_by_id(49233)
    print(show.ok().tags())
    from subsplease.display import display_details_jikan
    display_details_jikan(show.ok())
