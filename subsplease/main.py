from api import Subsplease
from display import display_schedule
from torrent import magnet
import subprocess


def main():
    subs = Subsplease()
    # res = subs.weekly_schedule()
    # display_schedule(res.unwrap().schedule.monday)
    res = subs.search("frieren")
    print(res.unwrap()[0])
    # display_schedule(res.unwrap())
    # latests = subs.latest()
    # latests = latests.unwrap()
    # magnet(latests[0], '480')


if __name__ == "__main__":
    main()
