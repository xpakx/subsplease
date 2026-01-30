import subprocess
from api import EpisodeData, DownloadData
from transmission_rpc import Client


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


def send_magnet_to_transmission(episode: EpisodeData, quality: str):
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

    except Exception as e:
        print(f"Error: {e}")
