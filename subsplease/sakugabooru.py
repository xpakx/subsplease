import msgspec
import requests
from subsplease.result import Result, Err, Ok
from enum import IntEnum
from pathlib import Path
import time


class SakugaTagType(IntEnum):
    GENERAL = 0
    ARTIST = 1
    COPYRIGHT = 3
    CHARACTER = 4
    METADATA = 5


class BooruTag(msgspec.Struct):
    id: int
    name: str
    count: int
    type: int
    ambiguous: bool


class BooruPost(msgspec.Struct):
    id: int
    tags: str
    created_at: int
    updated_at: int
    creator_id: int
    author: str
    source: str
    score: int
    file_size: int
    file_ext: str
    md5: str
    file_url: str


class SakugaBooruAPI:
    def __init__(self):
        self.url = "https://www.sakugabooru.com/"

    def search_tag(self, name: str) -> Result[list[BooruTag], str]:
        response = requests.get(
                f"{self.url}tag.json", params={
                    "name": name,
                    "type": SakugaTagType.COPYRIGHT,
                    "order": "name"
                })

        if response.status_code != 200:
            return Err(f"Sakugabooru API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=list[BooruTag]
            )
            return Ok(data)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def find_posts(self, tag: str, limit: int = 10):
        response = requests.get(
                f"{self.url}post.json", params={
                    "tags": tag,
                    "limit": limit
                })
        if response.status_code != 200:
            return Err(f"Sakugabooru API Error: {response.status_code}")

        try:
            data = msgspec.json.decode(
                    response.content,
                    type=list[BooruPost]
            )
            return Ok(data)
        except msgspec.DecodeError as e:
            return Err(f"Decode error: {e}")

    def download_images(
            self,
            posts: list[BooruPost],
            target_dir: str | None = None) -> None:
        save_path = Path(target_dir) if target_dir else Path.cwd()
        save_path.mkdir(parents=True, exist_ok=True)
        for post in posts:
            file_dest = save_path / f"{post.id}.mp4"
            if file_dest.exists():
                print(f"File {post.id} already downloaded")
                continue
            print(f"Downloading {post.id} to {file_dest}...")
            r = requests.get(post.file_url)
            file_dest.write_bytes(r.content)
            time.sleep(1)


if __name__ == "__main__":
    meta = SakugaBooruAPI()
    tags = meta.search_tag('tongari_boushi_no_atelier')
    print(tags)
    tag = tags.unwrap()[0]
    posts = meta.find_posts(tag.name).unwrap()
    print(posts[0])
    meta.download_images(posts)
