from api import Subsplease
from display import display_schedule
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
import subprocess
import time


def main():
    subs = Subsplease()
    res = subs.schedule()
    # display_schedule(res.unwrap().schedule.monday)
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    display_schedule(res.unwrap())
    # latests = subs.latest()
    # latests = latests.unwrap()
    # magnet(latests[0], '480')
    meta = MetadataProvider()
    result = meta.search_show("frieren")
    show = result.unwrap()
    print(show.title.english)
    print(show.title.romaji)
    print(show.title.native)
    db = AnimeDB()
    for item in res.unwrap().schedule:
        db.create_entry(item.page, item.title)



if __name__ == "__main__":
    main()
