from api import Subsplease
from display import display_schedule
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
import subprocess
import time


def main():
    meta = MetadataProvider()
    db = AnimeDB()
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
    subs = Subsplease()
    res = subs.schedule()
    today_shows = res.unwrap().schedule
    for show in today_shows:
        local = current.get(show.page)
        if not local:
            db.create_entry(show.page, show.title)
        if local and not local.anilist_id:
            print("Fetching")
            result = meta.search_show(show.title)
            if result.is_ok():
                ani_list_show = result.ok()
                local.title_english = ani_list_show.title.english
                local.title_japanese = ani_list_show.title.native
                local.anilist_id = ani_list_show.id
                db.update_show(local)

    # display_schedule(res.unwrap().schedule.monday)
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    display_schedule(res.unwrap(), current)
    # latests = subs.latest()
    # latests = latests.unwrap()
    # magnet(latests[0], '480')



if __name__ == "__main__":
    main()
