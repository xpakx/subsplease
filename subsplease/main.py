from api import Subsplease
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
from utils import today, schedule
from torrent import send_magnet_to_transmission
import subprocess
import time
import argparse


def main():
    pass
    # latests = subs.latest()
    # latests = latests.unwrap()
    # send_magnet_to_transmission(latests[0], '720')

    # display_schedule(res.unwrap().schedule.monday)
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    # magnet(latests[0], '480')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--tracked", action="store_true", help="Show only tracked")

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    today(meta, db, subs, only_tracked=args.tracked)
