import feedparser


def nyaa_newest(query: str):
    rss_url = f"https://nyaa.si/?page=rss&q={query}&c=1_2&f=0"
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        print(f"Title: {entry.title}")

        seeders = entry.get('nyaa_seeders', 'N/A')
        leechers = entry.get('nyaa_leechers', 'N/A')
        info_hash = entry.get('nyaa_infohash', 'N/A')
        size = entry.get('nyaa_size', 'N/A')

        print(f"Seeders: {seeders}: {leechers}")
        print(f"Leechers: {leechers}")
        print(f"Hash: {info_hash}")
        print(f"Size: {size}")
        print("-" * 20)
