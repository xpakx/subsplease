import msgspec
import requests
from result import Result, Err, Ok
from typing import Generic, TypeVar

T = TypeVar("T")


class AniListData(msgspec.Struct, Generic[T], rename='pascal'):
    media: T


class AniListResponse(msgspec.Struct, Generic[T]):
    data: AniListData[T]


class AniListTitle(msgspec.Struct):
    romaji: str | None
    english: str | None
    native: str | None


class AniListMedia(msgspec.Struct):
    id: int
    title: AniListTitle


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
            # TODO: typing

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
                else:
                    mapped_results[show.id] = None

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
