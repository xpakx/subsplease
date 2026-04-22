import subprocess
from subsplease.api import EpisodeData, DownloadData
from transmission_rpc import Client
from pathlib import Path
import shutil


class TorrentAPI:
    def __init__(self):
        pass

    # TODO: get credentials from config
    def _get_client(self) -> Client:
        return Client(
                host="localhost",
                port=9091,
                username="test",
                password="test_password"
            )

    def get_torrents(self):
        return self._get_client().get_torrents()

    def get_torrent_details(self, torrent_id: int):
        return self._get_client().get_torrent(torrent_id)

    def remove_torrent(self, torrent_id: int, delete_data: bool = False):
        return self._get_client().remove_torrent(
                torrent_id, delete_data=delete_data)

    def magnet(self, episode: EpisodeData, quality: str):
        link = self.select_quality(episode, quality)
        if not link:
            return
        subprocess.run(["xdg-open", link.magnet])

    def select_quality(self, episode: EpisodeData, quality: str) -> DownloadData | None:
        downloads = episode.downloads
        for link in downloads:
            if link.res == quality:
                return link
        return None

    def send_magnet_to_transmission(self, episode: EpisodeData, quality: str) -> str | None:
        link = self.select_quality(episode, quality)
        if not link:
            return

        try:
            c = self._get_client()
            new_torrent = c.add_torrent(link.magnet)
            print(f"Success! Added torrent: {new_torrent.name}")
            print(f"ID: {new_torrent.id}")
            print(f"ID: {new_torrent.hash_string}")
            return new_torrent.hash_string

        except Exception as e:
            print(f"Error: {e}")

    def check_torrent(self, torrent_id: int) -> bool:
        try:
            c = self._get_client()
            torrent = c.get_torrent(torrent_id)
            print(f"Found torrent: {torrent.name}")
            is_done = torrent.percent_done == 1.0
            if is_done:
                print("Torrent finished")
                return True
            else:
                print(f"Done {torrent.percent_done * 100:.2f}%")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    # TODO: join with normal check
    def check_torrent_corrupted(self, torrent_id: int) -> bool:
        try:
            c = self._get_client()
            c.get_torrent(torrent_id)
            return False
        except KeyError:
            return True
        except Exception:
            return False

    def list_torrents(self):
        try:
            c = self._get_client()
            torrents = c.get_torrents()
            for torrent in torrents:
                print(f"[{torrent.id}] {torrent.name}")
                is_done = torrent.percent_done == 1.0
                if is_done:
                    print("Done.")
        except Exception as e:
            print(f"Error: {e}")

    def move_torrent(self, torrent_id: int, dist: str, remove: bool = False):
        try:
            c = self._get_client()
            torrent = c.get_torrent(torrent_id)
            is_done = torrent.percent_done == 1.0
            if not is_done:
                return

            path = Path(torrent.download_dir) / torrent.name
            print(path)
            dest_dir = Path.home() / "Videos" / "TV Series" / dist
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"Moving data to {dest_dir} and updating Transmission path...")
            if not remove:
                c.move_torrent_data(torrent_id, str(dest_dir))
            else:
                shutil.move(str(path), str(dest_dir / torrent.name))
                c.remove_torrent(torrent_id, delete_data=False)
                print("Torrent removed from client")
        except Exception as e:
            print(f"Error: {e}")
