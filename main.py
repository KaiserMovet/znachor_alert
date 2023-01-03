import sys

import wykop

from app import EPG, TVParser
from app.pictures import Pictures


def get_wykop():
    api = wykop.WykopAPI(
        sys.argv[1],
        sys.argv[2],
    )
    api.authenticate(sys.argv[3])
    return api


def get_emmissions():
    tv_parser = TVParser(EPG().tree)
    return tv_parser.get_all_elements("Znachor")


def generate_wykop_entry(emissions) -> str:
    entry = ""
    if not emissions:
        entry += f"W ciągu najbliższych 5 dni nie odbędzie się żadna emisja Znachora :c\n"
    else:
        entry += f"W ciągu najbliższych 5 dni znachora będziemy mogli obejrzeć {len(emissions)} razy:\n"
        entry += "\n".join([em.msg for em in emissions])
        entry += "\n"

    header = "=== ZNACHOR ALERT!!! ===\n"
    footer = (
        "\n===\n"
        "Jestem Botem przypominającym o emisjach Znachora w ciągu "
        "najbliższych 5 dni. Wpis będzie tworzony raz na 4 dni.\n"
        "Jeśli coś nie działa jak powinno "
        "(zła godzina, coś zostało pominięte, etc.) "
        "dawajcie znać w komentarzach albo pw. Dzięki\n"
        "#znachor #znachoralert"
    )
    return f"{header}\n{entry}\n{footer}"


def add_wykop_entry(api, entry) -> None:
    res = api.entry_add(entry, Pictures.get_picture())
    print(f"Created entry: https://www.wykop.pl/wpis/{res.get('id')}")


def main() -> None:
    em = get_emmissions()
    msg = generate_wykop_entry(em)
    api = get_wykop()
    add_wykop_entry(api, msg)


if __name__ == "__main__":
    main()
