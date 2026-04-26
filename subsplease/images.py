from subsplease.db import LocalShow
from subsplease.sakugabooru import SakugaBooruAPI


class ImageService:
    def __init__(self, sakuga: SakugaBooruAPI):
        self.sakuga = sakuga

    def get_clips(self, show: LocalShow) -> None:
        formatted_name = show.title_romaji.lower().replace(" ", "_")
        tags = self.sakuga.search_tag(formatted_name)
        # TODO: save tag in repo
        if tags.is_err():
            print(f"Couldn't find sakugabooru tag for {show.title_english}")
            return
        tag_list = tags.unwrap()
        if len(tag_list) == 0:
            print(f"No clips yet for {show.title_english}")
            return
        tag = tag_list[0]
        posts = self.sakuga.find_posts(tag.name).unwrap()
        self.sakuga.download_images(posts)
