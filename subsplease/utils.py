from subsplease.api import Subsplease, ScheduleEntry, EpisodeData
from subsplease.metadata import MetadataProvider
from subsplease.db import AnimeDB, LocalShow, LocalEpisode
from subsplease.display import (
        display_schedule,
        display_latest,
        display_details
)
import re
import unicodedata
from subsplease.torrent import (
        check_torrent,
        check_torrent_corrupted,
        move_torrent,
        send_magnet_to_transmission
)
from rapidfuzz import process, fuzz
from rapidfuzz.utils import default_process
from pathlib import Path
import shutil
from rich.prompt import Confirm


class Program:
    def __init__(self, api: Subsplease,
                 meta: MetadataProvider, db: AnimeDB):
        self.subs = api
        self.meta = meta
        self.db = db
        self.only_tracked = False
        self.current: dict[str, LocalShow] = {}

    def load_shows(self):
        airing = self.db.get_airing_shows().unwrap()
        self.current = {x.sid: x for x in airing}

    def switch_only_tracked(self, value: bool):
        self.only_tracked = value

    def fetch_show(self, title: str, show: LocalShow):
        print("Fetching")
        result = self.meta.search_show(title)
        if result.is_ok():
            ani_list_show = result.unwrap()
            show.title_english = ani_list_show.title.english
            show.title_japanese = ani_list_show.title.native
            show.anilist_id = ani_list_show.id
            show.dir_name = self.get_show_dir(show)
            self.db.update_show(show)

    def show_schedule(self):
        res = self.subs.weekly_schedule().unwrap()
        for day_name, day_list in res.schedule:
            print(day_name)
            display_schedule(day_list, self.current)

    def latest(self):
        episodes = self.subs.latest()
        display_latest(episodes.unwrap(), self.current, self.only_tracked)

    def view_show(self, title: str):
        print(f"Searching '{title}'")
        result = self.meta.search_show_details(title).unwrap()
        display_details(result)

    def get_show_dir(self, show: LocalShow) -> str | None:
        name = show.title_english or show.title_romaji
        if not name:
            return
        name = re.sub(r'(?i)\s*season\s+\d+', '', name)
        name = re.sub(r'(?i)\s*s\d+\b', '', name)
        if ': ' in name:
            name = name.split(': ', maxsplit=1)[0]

        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ascii', 'ignore').decode('ascii')
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        name = name.strip('.')

        if not name or name.isspace():
            return

        if name.isupper():
            name = name.title()

        return name

    def get_local_show(self, id: int) -> LocalShow | None:
        for show in self.current.values():
            if show.id == id:
                return show
        return None

    def check_downloads(self):
        eps = self.db.get_unfinished_downloads().unwrap()
        for ep in eps:
            show = self.get_local_show(ep.show_id)
            if not show:
                continue
            if not show.dir_name:
                continue
            print(ep.episode, show.title_english)
            finished = check_torrent(ep.torrent_hash)
            if finished:
                move_torrent(ep.torrent_hash, show.dir_name)
                ep.downloaded = True
                self.db.update_episode(ep)

    def fix_torrents(self):
        eps = self.db.get_unfinished_downloads().unwrap()
        for ep in eps:
            corrupted = check_torrent_corrupted(ep.torrent_hash)
            if corrupted:
                print("Found corrupted torrent")
                print(ep.show_id, ep.episode)
                ep.torrent_hash = None
                self.db.update_episode(ep)

    def select_show(self, query: str):
        options = [self.current[x].title_english for x in self.current.keys()]
        best_match = process.extractOne(
                query,
                options,
                processor=default_process,
                scorer=fuzz.WRatio)
        if best_match:
            _, _, index = best_match
            key = list(self.current.keys())[index]
            return self.current.get(key)

    def show(self, query: str):
        show = self.select_show(query)
        if not show:
            return
        print(show.title_english)
        if not show:
            return
        show_id = show.subsplease_id
        if not show_id:
            show_id = self.subs.get_sid(show.sid).unwrap()
            show.subsplease_id = show_id
            self.db.update_show(show)
        print(show_id)
        data = self.subs.show(show_id)
        episodes = list(data.unwrap().episode.values())
        display_latest(episodes, self.current)

    def start_download(self, id: int, quality: str):
        data = self.subs.latest()
        print(len(data.unwrap()))
        data = [show for show in data.unwrap() if show.time == 'New']
        show = data[id]
        hash = send_magnet_to_transmission(show, quality)
        if not hash:
            return
        local = self.current.get(show.page)
        if not local:
            return
        print(local.title_english)
        r = self.db.create_episode(local.id, int(show.episode), hash)
        print(r)

    def select(self, query: str):
        self.selection = self.select_show(query)

    def is_show_selected(self):
        return self.selection is not None

    def subscribe(self, track: bool = True):
        show = self.selection
        if not show:
            return
        print(show.title_english)
        show = self.db.toggle_tracking(show.sid, track)

    def view_selected_show(self):
        show = self.selection
        if not show:
            return
        if not show.anilist_id:
            # TODO: get id
            return
        result = self.meta.search_show_details_by_id(show.anilist_id).unwrap()
        display_details(result)

    def find_and_get_episode(self, ep: int):
        show = self.selection
        if not show:
            return
        show_id = show.subsplease_id
        if not show_id:
            show_id = self.subs.get_sid(show.sid).unwrap()
            show.subsplease_id = show_id
            self.db.update_show(show)
        data = self.subs.show(show_id)
        episodes = list(data.unwrap().episode.values())
        episode_to_get = None
        episode_num = None
        for episode in episodes:
            num = episode.episode
            if not num.isdigit():
                num = num.split('v')[0]
            if not num.isdigit():
                continue
            num = int(num)
            if num != ep:
                continue
            episode_to_get = episode
            episode_num = num
            break
        # print(episode_to_get)
        if not episode_to_get or not episode_num:
            print("Couldn't find episode")
            return

        local = self.db.get_episode(show.id, episode_num)
        if local.is_ok():
            print("already downloaded")
            return

        hash = send_magnet_to_transmission(episode_to_get, "720")
        if not hash:
            return
        print(show.title_english)
        r = self.db.create_episode(show.id, episode_num, hash)

        print(r)
        if episode_num > show.last_episode:
            show.last_episode = episode_num
            self.db.update_show(show)

    def show_episodes(self):
        show = self.selection
        if not show:
            return
        print(show.title_english)
        show_id = show.subsplease_id
        if not show_id:
            show_id = self.subs.get_sid(show.sid).unwrap()
            show.subsplease_id = show_id
            self.db.update_show(show)
        print(show_id)
        data = self.subs.show(show_id)
        episodes = list(data.unwrap().episode.values())
        display_latest(episodes, self.current)

    def find_get_new_episodes(self):
        show = self.selection
        if not show:
            return
        show_id = show.subsplease_id
        if not show_id:
            show_id = self.subs.get_sid(show.sid).unwrap()
            show.subsplease_id = show_id
            self.db.update_show(show)
        data = self.subs.show(show_id)
        episodes = list(data.unwrap().episode.values())
        print([x.episode for x in episodes])
        downloaded = self.db.get_downloaded_for_show(show.id).unwrap()
        if len(downloaded) > 0:
            max_episode = max([x.episode for x in downloaded])
        else:
            max_episode = -1
        print(max_episode)
        episodes = [x for x in episodes if self.later_than(x, max_episode)]
        print([x.episode for x in episodes])

        show_updated = False
        for episode in episodes:
            hash = send_magnet_to_transmission(episode, "720")
            if not hash:
                return
            print(show.title_english)
            episode_num = self.get_num(episode)
            r = self.db.create_episode(show.id, episode_num, hash)
            if episode_num > show.last_episode:
                show.last_episode = episode_num
                show_updated = True
            print(r)

        if show_updated:
            self.db.update_show(show)

    def get_num(self, episode: EpisodeData) -> int:
        num = episode.episode
        if not num.isdigit():
            num = num.split('v')[0]
        return int(num)

    def later_than(self, episode: EpisodeData, max_ep: int) -> bool:
        num = episode.episode
        if not num.isdigit():
            num = num.split('v')[0]
        if not num.isdigit():
            return False
        num = int(num)
        return num > max_ep

    def delete_show(self):
        show = self.selection
        if not show:
            return
        show_id = show.subsplease_id
        if not show_id:
            show_id = self.subs.get_sid(show.sid).unwrap()
            show.subsplease_id = show_id
            self.db.update_show(show)
        show_dir = Path.home() / "Videos" / "TV Series" / show.dir_name

        if not show_dir.exists():
            print(f"Folder {show_dir} not found.")
            return

        print(
                f"Deleting {show_dir}."
        )
        proceed = Confirm.ask("Are you sure?")
        if not proceed:
            return
        try:
            shutil.rmtree(show_dir)
            print("Folder removed successfully.")
        except OSError as e:
            print(f"Error: {e.strerror}")


class DayService:
    def __init__(self, api: Subsplease,
                 meta: MetadataProvider, db: AnimeDB,
                 program: Program
                 ):
        self.subs = api
        self.meta = meta
        self.db = db
        self.program = program

    def today(self):
        res = self.subs.schedule()
        today_shows = res.unwrap().schedule
        self.update_local(today_shows)

        display_schedule(
                res.unwrap(),
                self.program.current,
                self.program.only_tracked
        )

    def update_local(self, shows: list[ScheduleEntry]):
        for show in shows:
            self.update_or_create_local_show(show)

    def update_or_create_local_show(
            self, show: ScheduleEntry
    ) -> LocalShow | None:
        local = self.program.current.get(show.page)
        if not local:
            self.db.create_entry(show.page, show.title)
        if local and not local.anilist_id:
            # TODO: repo???
            self.program.fetch_show(show.title, local)
        return local

    def show_day(self, day: str):
        res = self.subs.weekly_schedule()
        week = res.unwrap().schedule
        day_list = week.get_day(day)
        if not day_list:
            return
        self.update_local(day_list)

        print(day.capitalize())
        display_schedule(day_list, self.program.current)

    # TODO: move
    def update_schedule(self):
        res = self.subs.weekly_schedule().unwrap()
        for day_name, day_list in res.schedule:
            print(f"Updating {day_name.title()}")
            self.update_local(day_list)
