from api import Subsplease
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
from utils import today
import subprocess
import time


def main():
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    today(meta, db, subs)
    

    # display_schedule(res.unwrap().schedule.monday)
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    # latests = subs.latest()
    # latests = latests.unwrap()
    # magnet(latests[0], '480')



if __name__ == "__main__":
    main()
