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
            data = msgspec.json.decode(response.content, type=AniListResponse)
            return Ok(data.data.Media)
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
            raw_data = msgspec.json.decode(response.content)
            data_block = raw_data.get("data", {})

            mapped_results = {}
            for index, original_title in enumerate(titles):
                key = f"s{index}"
                if key in data_block and data_block[key] is not None:
                    mapped_results[original_title] = data_block[key]
                else:
                    mapped_results[original_title] = None

            return Ok(mapped_results)

        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")
