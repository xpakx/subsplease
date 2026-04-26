from subsplease.db import LocalShow
from subsplease.sakugabooru import SakugaBooruAPI
from subsplease.db import AnimeDB


class ImageService:
    def __init__(self, sakuga: SakugaBooruAPI, db: AnimeDB):
        self.sakuga = sakuga
        self.db = db

    def get_tag(self, show: LocalShow) -> str | None:
        formatted_name = show.title_romaji.lower().replace(" ", "_")
        tags = self.sakuga.search_tag(formatted_name)
        if tags.is_err():
            print(f"Couldn't find sakugabooru tag for {show.title_english}")
            return
        tag_list = tags.unwrap()
        if len(tag_list) == 0:
            print(f"No clips yet for {show.title_english}")
            return
        tag = tag_list[0]
        return tag.name

    def get_clips(self, show: LocalShow) -> None:
        if not show.sakugaboru_tag:
            print("no tag yet")
            # TODO sometimes romaji title in our db is shortend
            # title, while sakugabooru actually uses long title
            print(show.title_romaji)
            tag = self.get_tag(show)
            if not tag:
                return
            show.sakugaboru_tag = tag
            self.db.update_show(show)
        else:
            print(f"has tag: {show.sakugaboru_tag}")
            tag = show.sakugaboru_tag
        if not tag:
            print(f"Couldn't find sakugabooru tag for {show.title_english}")

        posts = self.sakuga.find_posts(tag).unwrap()
        self.sakuga.download_images(posts)
