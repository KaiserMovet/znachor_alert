import datetime
import json
import sys
from typing import List

import wykop

from app import EPG, Emission, TVParser
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


def generate_wykop_entry(emissions: List[Emission], counter: int) -> str:
    emissions = [e for e in emissions if not e.already_took_place()]
    dates_str = ""
    dates_str = f"({datetime.datetime.now().strftime('%d.%m')} - {(datetime.datetime.now()+datetime.timedelta(days=4)).strftime('%d.%m')})"
    entry = ""
    if not emissions:
        entry += f"W ciągu najbliższych 5 dni {dates_str} nie odbędzie się żadna emisja Znachora :c\n"
    else:
        entry += f"W ciągu najbliższych 5 dni {dates_str} znachora będziemy mogli obejrzeć {len(emissions)} razy:\n"
        entry += "\n".join([em.msg for em in emissions])
        entry += "\n"

    header = f"=== ZNACHOR ALERT!!! {counter}/∞ ===\n"
    footer = (
        "\n===\n"
        "Jestem Botem przypominającym o emisjach Znachora w ciągu "
        "najbliższych 5 dni. Wpis będzie tworzony raz na 4 dni lub szybciej (pewnie szybciej xd).\n"
        "Jeśli coś nie działa jak powinno "
        "(zła godzina, coś zostało pominięte, etc.) "
        "dawajcie znać w komentarzach albo pw. Dzięki\n"
        "https://github.com/KaiserMovet/znachor_alert\n"
        "#znachor #znachoralert"
    )
    return f"{header}\n{entry}\n{footer}"


def add_wykop_entry(api, entry) -> None:
    res = api.entry_add(entry, Pictures.get_picture())
    print(f"Created entry: https://www.wykop.pl/wpis/{res.get('id')}")


def add_emissions_to_history(emissions: List[Emission]) -> None:
    with open("history.json", "r") as f:
        full_data = json.load(f)
    data = full_data.get("emissions", [])
    if not data:
        data = []
    current_id = [em["id"] for em in data]

    for em in emissions:
        em_dict = em.to_dict()
        if not em_dict["id"] in current_id:
            data.append(em_dict)

    data.sort(key=lambda x: x["start"])
    full_data["emissions"] = data
    with open("history.json", "w") as f:
        f.write(json.dumps(full_data, indent=4))


def get_counter() -> int:
    with open("history.json", "r") as f:
        full_data = json.load(f)
    counter = full_data.get("counter", 0)
    counter += 1
    full_data["counter"] = counter
    with open("history.json", "w") as f:
        f.write(json.dumps(full_data, indent=4))
    return counter


def main() -> None:
    em = get_emmissions()
    add_emissions_to_history(em)
    counter = get_counter()
    msg = generate_wykop_entry(em, counter)
    api = get_wykop()
    # add_wykop_entry(api, msg)
    print(msg)


if __name__ == "__main__":
    main()
