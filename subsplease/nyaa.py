import feedparser
from urllib import parse
from subsplease.result import Result, Ok
from dataclasses import dataclass
from typing import cast


@dataclass
class NyaaTorrent:
    title: str
    seeders: str
    leechers: str
    size: str
    magnet: str


def create_magnet(info_hash, title):
    magnet_data = {
        'xt': f'urn:btih:{info_hash}',
        'dn': title,
        'tr': [
            'http://nyaa.tracker.wf:7777/announce',
            'udp://open.stealth.si:80/announce',
            'udp://tracker.opentrackr.org:1337/announce',
            'udp://exodus.desync.com:6969/announce',
            'udp://tracker.torrent.eu.org:451/announce'
        ]
    }
    return f"magnet:?{parse.urlencode(magnet_data, doseq=True)}"


def nyaa_newest(query: str, quality: int | None = None
                ) -> Result[list[NyaaTorrent], str]:
    if quality:
        query += f" {quality}p"
    print(query)
    query = parse.quote_plus(query)
    rss_url = f"https://nyaa.si/?page=rss&q={query}&c=1_2&f=0"
    feed = feedparser.parse(rss_url)
    results = []

    for entry in feed.entries:
        print(f"Title: {entry.title}")

        seeders = cast(str, entry.get('nyaa_seeders', 'N/A'))
        leechers = cast(str, entry.get('nyaa_leechers', 'N/A'))
        info_hash = cast(str, entry.get('nyaa_infohash', 'N/A'))
        size = cast(str, entry.get('nyaa_size', 'N/A'))
        title = cast(str, entry.title)

        results.append(
                NyaaTorrent(
                    title=title,
                    seeders=seeders,
                    leechers=leechers,
                    size=size,
                    magnet=create_magnet(info_hash, entry.title)
                )
        )
    print(results)
    return Ok(results)
