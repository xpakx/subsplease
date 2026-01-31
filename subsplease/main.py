from api import Subsplease
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
from utils import today, schedule
from torrent import send_magnet_to_transmission
from display import display_schedule
import subprocess
import time
import argparse


def main():
    pass
    # send_magnet_to_transmission(latests[0], '720')
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    # magnet(latests[0], '480')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--tracked", action="store_true", help="Show only tracked")
    parser.add_argument("-l", "--latest", action="store_true", help="Get latest episodes")
    parser.add_argument("-w", "--weekly", action="store_true", help="Show weekly schedule")

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    if args.latest:
        data = subs.latest()
        print(data)
    elif args.weekly:
        data = subs.weekly_schedule()
        display_schedule(res.unwrap().schedule.monday)
    else:
        today(meta, db, subs, only_tracked=args.tracked)
