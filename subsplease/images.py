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
            return
        tag_list = tags.unwrap()
        if len(tag_list) == 0:
            return
        print(tag_list)
        tag = tag_list[0]
        posts = self.sakuga.find_posts(tag.name).unwrap()
        print(posts[0])
        self.sakuga.download_images(posts)
