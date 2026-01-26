import subprocess
from api import EpisodeData, DownloadData


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
