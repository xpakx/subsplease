from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from display import display_schedule


def today(meta: MetadataProvider, db: AnimeDB, subs: Subsplease):
    airing = db.get_airing_shows().unwrap()
    current = {x.sid: x for x in airing}
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
    display_schedule(res.unwrap(), current)
