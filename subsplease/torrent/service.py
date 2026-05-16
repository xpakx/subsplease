from subsplease.seadex import Seadex
from subsplease.nyaa import nyaa_newest
from subsplease.config import Config


class TorrentSearchService:
    def __init__(self, config: Config, seadex: Seadex):
        self.seadex = seadex
        self.default_quality = config.preferred_quality

    def search(self, name: str):
        # seadex uses anilist id
        result = nyaa_newest(name, self.default_quality).unwrap()
        for entry in result:
            print(entry.title)
            print(entry.size)
            print()

    def search_seadex(self, show_id: int):
        data = self.seadex.schedule(show_id)
        if data.is_err():
            return
        items = data.unwrap().items
        if len(items) == 0:
            return
        entries = items[0].expand.trs
        for entry in entries:
            print(entry.tracker)
            print(entry.infoHash)
            print(entry.url)
            print(entry.created)
            print(entry.size())
            print()
