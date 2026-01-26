from api import Subsplease


def main():
    subs = Subsplease()
    res = subs.schedule('Europe/Warsaw')
    print(res)


if __name__ == "__main__":
    main()
