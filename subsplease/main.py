from api import Subsplease
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
from utils import today
import subprocess
import time
from torrent import send_magnet_to_transmission


def main():
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    today(meta, db, subs)

    # latests = subs.latest()
    # latests = latests.unwrap()
    # send_magnet_to_transmission(latests[0], '720')

    # display_schedule(res.unwrap().schedule.monday)
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    # magnet(latests[0], '480')


if __name__ == "__main__":
    main()
