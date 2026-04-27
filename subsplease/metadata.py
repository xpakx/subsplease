import msgspec
import requests
from subsplease.result import Result, Err, Ok
from typing import Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class AniListData(msgspec.Struct, Generic[T], rename='pascal'):
    media: T


class AniListResponse(msgspec.Struct, Generic[T]):
    data: AniListData[T]


class AniListDataPage(msgspec.Struct, Generic[T]):
    media: T


class AniListDataPaged(msgspec.Struct, Generic[T], rename='pascal'):
    page: AniListDataPage[T]


class AniListResponsePaged(msgspec.Struct, Generic[T]):
    data: AniListDataPaged[T]


class AniListTitle(msgspec.Struct):
    romaji: str | None
    english: str | None
    native: str | None


class AniListMedia(msgspec.Struct):
    id: int
    title: AniListTitle


class AniListMediaAlts(msgspec.Struct):
    synonyms: list[str]


class AniListTag(msgspec.Struct):
    name: str


class AniListAiring(msgspec.Struct):
    airingAt: int
    episode: int


class AniListMediaDetails(msgspec.Struct):
    id: int
    title: AniListTitle
    description: str
    status: str
    nextAiringEpisode: AniListAiring | None
    tags: list[AniListTag]


class AniTitles(msgspec.Struct):
    data: dict[str, AniListMedia]


class MetadataProvider:
    def __init__(self):
        self.url = "https://graphql.anilist.co/"

    def search_show(self, query: str) -> Result[AniListMedia, str]:
        query = query.replace('(JP)', '')
        query_string = """
        query ($search: String) {
          Media (search: $search, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
          }
        }
        """

        response = requests.post(
            self.url,
            json={'query': query_string, 'variables': {'search': query}}
        )

        if response.status_code != 200:
            return Err(f"AniList API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=AniListResponse[AniListMedia]
            )
            return Ok(data.data.media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def fetch_titles(self, titles: list[str]) -> Result[dict, str]:
        query_parts = []

        fragment = """
            id
            title {
                romaji
                english
                native
            }
        """

        for index, title in enumerate(titles):
            safe_title = title.replace('"', '\\"')

            part = f's{index}: Media(search: "{safe_title}", type: ANIME) {{ {fragment} }}'
            query_parts.append(part)

        full_query = "query { " + " ".join(query_parts) + " }"

        response = requests.post(
            self.url,
            json={'query': full_query}
        )

        if response.status_code != 200:
            return Err(f"AniList API Error: {response.text}")

        try:
            print(response.content)
            data = msgspec.json.decode(
                    response.content,
                    type=AniTitles
            )
            data_block = data.data

            mapped_results = {}
            for index, show in enumerate(data_block.values()):
                key = f"s{index}"
                if key in data_block and data_block[key] is not None:
                    mapped_results[show.id] = show

            return Ok(mapped_results)

        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def search_show_details(
            self, query: str) -> Result[AniListMediaDetails, str]:
        query = query.replace('(JP)', '')
        query_string = """
        query ($search: String) {
          Media (search: $search, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description(asHtml: false)
            status
            nextAiringEpisode {
              airingAt
              episode
            }
            tags { name }
          }
        }
        """

        response = requests.post(
            self.url,
            json={'query': query_string, 'variables': {'search': query}}
        )

        if response.status_code != 200:
            return Err(f"AniList API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=AniListResponse[AniListMediaDetails]
            )
            return Ok(data.data.media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def search_show_details_by_id(
            self, id: int) -> Result[AniListMediaDetails, str]:
        query_string = """
        query ($mediaId: Int) {
          Media (id: $mediaId, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description(asHtml: false)
            status
            nextAiringEpisode {
              airingAt
              episode
            }
            tags { name }
          }
        }
        """

        response = requests.post(
            self.url,
            json={'query': query_string, 'variables': {'mediaId': id}}
        )

        if response.status_code != 200:
            print(response.content)
            return Err(f"AniList API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=AniListResponse[AniListMediaDetails]
            )
            return Ok(data.data.media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def _season_name(self) -> tuple[str, int]:
        now = datetime.now()
        year = now.year
        month = now.month
        if month in [1, 2, 3]:
            return "WINTER", year
        elif month in [4, 5, 6]:
            return "SPRING", year
        elif month in [7, 8, 9]:
            return "SUMMER", year
        else:
            return "FALL", year

    def get_current_season_summary(self):
        season, year = self._season_name()

        query = """
        query ($season: MediaSeason, $seasonYear: Int) {
          Page(page: 1, perPage: 50) {
            media(season: $season, seasonYear: $seasonYear, type: ANIME, sort: POPULARITY_DESC) {
              id
              title {
                romaji
                english
                native
              }
              description(asHtml: false)
              status
              nextAiringEpisode {
                  airingAt
                  episode
                  }
              tags { name }
            }
          }
        }
        """

        response = requests.post(
            self.url,
            json={
                'query': query,
                'variables': {'season': season, "seasonYear": year}
            }
        )

        if response.status_code != 200:
            print(response.content)
            return Err(f"AniList API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=AniListResponsePaged[list[AniListMediaDetails]]
            )
            return Ok(data.data.page.media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def get_alt_titles(self, ani_id: int) -> Result[list[str], str]:
        query_string = """
        query ($id: Int) {
          Media (id: $id, type: ANIME) {
              synonyms
          }
        }
        """

        response = requests.post(
            self.url,
            json={'query': query_string, 'variables': {'id': ani_id}}
        )

        if response.status_code != 200:
            return Err(f"AniList API Error: {response.status_code}")

        try:
            print(response.content)
            data = msgspec.json.decode(
                    response.content,
                    type=AniListResponse[AniListMediaAlts]
            )
            return Ok(data.data.media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")


if __name__ == "__main__":
    meta = MetadataProvider()
    print(meta.get_alt_titles(147105).unwrap())
