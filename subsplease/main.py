from api import Subsplease
from display import display_schedule


def main():
    subs = Subsplease()
    res = subs.schedule('Europe/Warsaw')
    display_schedule(res.unwrap())


if __name__ == "__main__":
    main()
