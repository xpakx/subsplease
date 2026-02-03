from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from utils import (
        latest, update_schedule, show_day, view_show,
        Program
)
from torrent import send_magnet_to_transmission
import argparse


def main():
    pass
    # send_magnet_to_transmission(latests[0], '720')
    # res = subs.search("frieren")
    # print(res.unwrap()[0])
    # magnet(latests[0], '480')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
            "-t", "--tracked", action="store_true",
            help="Show only tracked")
    parser.add_argument(
            "-l", "--latest", action="store_true",
            help="Get latest episodes")
    parser.add_argument(
            "-u", "--update", action="store_true",
            help="Update weekly schedule")
    parser.add_argument(
            '-d', '--download', type=int,
            help="Id to download")
    parser.add_argument(
            '-q', '--quality', type=int,
            default=720, help="Quality to download")
    parser.add_argument(
            '-s', '--subscribe', type=int,
            help="Id to subscribe")
    parser.add_argument(
            '-w', '--weekday', type=str,
            help="Day to show")
    parser.add_argument(
            '-v', '--view', type=str,
            help="Show to view")

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.switch_only_tracked(args.tracked)

    id = args.download
    if id is not None:
        data = subs.latest()
        print(len(data.unwrap()))
        data = [show for show in data.unwrap() if show.time == 'New']
        show = data[id]
        send_magnet_to_transmission(show, str(args.quality))
        exit(0)
    id = args.subscribe
    if id is not None:
        data = subs.schedule().unwrap().schedule
        show = data[id]
        show = db.toggle_tracking(show.page, True)
        exit(0)
    to_view = args.view
    if to_view is not None:
        view_show(meta, db, to_view)
        exit(0)

    if args.latest:
        latest(meta, db, subs, only_tracked=args.tracked)
    elif args.weekday:
        show_day(meta, db, subs, args.weekday)
    elif args.update:
        update_schedule(meta, db, subs)
    else:
        program.today()
