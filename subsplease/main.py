from api import Subsplease
from torrent import magnet
from metadata import MetadataProvider
from db import AnimeDB
from utils import today, schedule, latest
from torrent import send_magnet_to_transmission
from display import display_schedule, display_latest
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
    parser.add_argument('-d', '--download', type=int, help="Id to download")
    parser.add_argument('-q', '--quality', type=int, default=720, help="Quality to download")

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    id = args.download
    if id is not None:
        data = subs.latest()
        print(len(data.unwrap()))
        data = [show for show in data.unwrap() if show.time == 'New']
        show = data[id]
        send_magnet_to_transmission(show, str(args.quality))
        exit(0)

    print(id)
    if args.latest:
        latest(meta, db, subs, only_tracked=args.tracked)
    elif args.weekly:
        data = subs.weekly_schedule()
        display_schedule(data.unwrap().schedule.monday)
    else:
        today(meta, db, subs, only_tracked=args.tracked)
