import subprocess
from subsplease.api import EpisodeData, DownloadData
from transmission_rpc import Client
from pathlib import Path
import shutil


def magnet(episode: EpisodeData, quality: str):
    link = select_quality(episode, quality)
    if not link:
        return
    subprocess.run(["xdg-open", link.magnet])


def select_quality(episode: EpisodeData, quality: str) -> DownloadData | None:
    downloads = episode.downloads
    for link in downloads:
        if link.res == quality:
            return link
    return None


def send_magnet_to_transmission(episode: EpisodeData, quality: str) -> str:
    link = select_quality(episode, quality)
    if not link:
        return

    try:
        c = Client(
                host='localhost',
                port=9091,
                username='test',
                password='test_password'
        )
        new_torrent = c.add_torrent(link.magnet)
        print(f"Success! Added torrent: {new_torrent.name}")
        print(f"ID: {new_torrent.id}")
        print(f"ID: {new_torrent.hash_string}")
        return new_torrent.hash_string

    except Exception as e:
        print(f"Error: {e}")


def check_torrent(torrent_id: int) -> bool:
    try:
        c = Client(
                host='localhost',
                port=9091,
                username='test',
                password='test_password'
        )
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


def list_torrents():
    try:
        c = Client(
                host='localhost',
                port=9091,
                username='test',
                password='test_password'
        )
        torrents = c.get_torrents()
        for torrent in torrents:
            print(f"[{torrent.id}] {torrent.name}")
            is_done = torrent.percent_done == 1.0
            if is_done:
                print("Done.")
    except Exception as e:
        print(f"Error: {e}")


def move_torrent(torrent_id: int, dist: str, remove: bool = False):
    try:
        c = Client(
                host='localhost',
                port=9091,
                username='test',
                password='test_password'
        )
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
