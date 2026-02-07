from api import Subsplease
from metadata import MetadataProvider
from db import AnimeDB
from utils import Program
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
    program.load_shows()
    program.switch_only_tracked(args.tracked)

    id = args.download
    if id is not None:
        data = subs.latest()
        print(len(data.unwrap()))
        data = [show for show in data.unwrap() if show.time == 'New']
        show = data[id]
        hash = send_magnet_to_transmission(show, str(args.quality))
        local = program.current.get(show.page)
        print(local.title_english)
        r = db.create_episode(local.id, int(show.episode), hash)
        print(r)
        exit(0)
    id = args.subscribe
    if id is not None:
        data = subs.schedule().unwrap().schedule
        show = data[id]
        show = db.toggle_tracking(show.page, True)
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
    else:
        program.today()
