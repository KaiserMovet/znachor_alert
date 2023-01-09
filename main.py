import argparse
import datetime
import json
from pprint import pprint
from typing import List

import wykop

from app import EPG, Emission, TVParser
from app.pictures import Pictures


def get_wykop(app_key, secret_key, account_key) -> wykop.WykopAPI:
    api = wykop.WykopAPI(
        app_key,
        secret_key,
    )
    api.authenticate(account_key)
    return api


def get_emmissions() -> list[Emission]:
    tv_parser = TVParser(EPG().tree)
    return tv_parser.get_all_elements("Znachor")


def generate_wykop_entry(emissions: List[Emission], counter: int) -> str:
    dates_str = ""
    now = datetime.datetime.now()
    dates_str = (
        f"({now.strftime('%d.%m')} - "
        f"{(now+datetime.timedelta(days=4)).strftime('%d.%m')})"
    )
    entry = ""
    if not emissions:
        entry += (
            f"W ciągu najbliższych 5 dni {dates_str} nie odbędzie się "
            "żadna emisja Znachora :c\n"
        )
    else:
        entry += (
            f"W ciągu najbliższych 5 dni {dates_str} znachora będziemy "
            "mogli obejrzeć {len(emissions)} razy:\n"
        )
        entry += "\n".join([em.msg for em in emissions])
        entry += "\n"

    header = f"=== ZNACHOR ALERT!!! {counter}/∞ ===\n"
    footer = (
        "\n===\n"
        "Jestem Botem przypominającym o emisjach Znachora w ciągu "
        "najbliższych 5 dni. Wpis będzie tworzony w co 4 dzień każdego "
        "miesiąca (1, 5, 9 itd.), jeśli odbywa się jakaś emisja.\n"
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


def get_counter(increment=True) -> int:
    with open("history.json", "r") as f:
        full_data = json.load(f)
    counter = full_data.get("counter", 0)
    if increment:
        counter += 1
        full_data["counter"] = counter
        with open("history.json", "w") as f:
            f.write(json.dumps(full_data, indent=4))
    return counter


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            f"Script will download data from {EPG.URL} "
            "and post entry on Wykop.pl"
        )
    )
    parser.add_argument(
        "--demo",
        help="Entry will be generated, but not published on Wykop.pl",
        action="store_true",
    )
    parser.add_argument(
        "--app-key",
        help="Wykop App key. Can be ignore, if --demo is set",
    )
    parser.add_argument(
        "--secret-key",
        help="Wykop secret key. Can be ignore, if --demo is set",
    )
    parser.add_argument(
        "--account-key",
        help="Wykop user account key. Can be ignore, if --demo is set",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    args = get_args()
    em = get_emmissions()
    pprint(em)
    future_em = [e for e in em if not e.already_took_place()]
    add_emissions_to_history(em)
    if future_em:
        counter = get_counter(increment=not args.demo)
        msg = generate_wykop_entry(future_em, counter)
        print(msg)
        if not args.demo:
            api = get_wykop(
                app_key=args.app_key,
                secret_key=args.secret_key,
                account_key=args.account_key,
            )
            add_wykop_entry(api, msg)
    else:
        print("No future emmissions")


if __name__ == "__main__":
    main()
