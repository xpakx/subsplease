from api import Subsplease
from display import display_schedule
from torrent import magnet
from metadata import MetadataProvider
import subprocess


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
    title = result.unwrap().title
    print(title.english)
    print(title.romaji)
    print(title.native)


if __name__ == "__main__":
    main()
