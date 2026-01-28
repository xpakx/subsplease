import msgspec
import requests
from result import Result, Err, Ok


class AniListTitle(msgspec.Struct):
    romaji: str | None
    english: str | None
    native: str | None


class AniListMedia(msgspec.Struct):
    id: int
    title: AniListTitle


class AniListData(msgspec.Struct):
    Media: AniListMedia


class AniListResponse(msgspec.Struct):
    data: AniListData


class MetadataProvider:
    def __init__(self):
        self.url = "https://graphql.anilist.co/"

    def search_show(self, query: str) -> Result[AniListMedia, str]:
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
            data = msgspec.json.decode(response.content, type=AniListResponse)
            return Ok(data.data.Media)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")
