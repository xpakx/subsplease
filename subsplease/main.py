from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from utils import Program
import argparse


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
    parser.add_argument(
            '-e', '--episodes', type=str,
            help="Show to see episodes of")

    args = parser.parse_args()
    meta = MetadataProvider()
    db = AnimeDB()
    subs = Subsplease()
    program = Program(subs, meta, db)
    program.load_shows()
    program.switch_only_tracked(args.tracked)

    id = args.download
    if id is not None:
        program.start_download(id, str(args.quality))
        exit(0)
    id = args.subscribe
    if id is not None:
        program.subscribe(id)
        exit(0)
    to_view = args.view
    if to_view is not None:
        program.view_show(to_view)
        exit(0)

    if args.latest:
        program.latest()
    elif args.weekday:
        program.show_day(args.weekday)
    elif args.update:
        program.update_schedule()
    elif args.episodes:
        program.show(args.episodes)
    else:
        program.today()
