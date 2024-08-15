import argparse
import datetime
import json
import random
from pprint import pprint
from typing import List

from pywykop3 import WykopAPI

from app import EPG, Emission, Entry, Movie, TVParser
from app.pictures import Pictures


def get_wykop(token: str) -> WykopAPI:
    api = WykopAPI(refresh_token=token)
    return api


def get_emmissions(movie: Movie) -> list[Emission]:
    tv_parser = TVParser(EPG().tree)
    return tv_parser.get_all_elements(movie)


def add_wykop_entry(api: WykopAPI, entry) -> None:
    photos = [
        "BwgVL0qM78zX2rZE134lYoaXpON6GNROvPnbQAWJamy6x9ed5D",
        "AXvwaN4mJeDVMWOZkzgYBokJAR7VGyn0916Rx5b7dq2lpPL8Qr",
        "8BAYbzlEea93RL2VrMy6dj1nAeyWGXvmpq05n4DO7ZNxgJwQkP",
        "XWgv4DMRam7LyPqpxAO2zo9J5gy3K9QBwEVYdNr1l3086bnkJZ",
        "VPq197R6zlBmJXW3Q5OZwGNpDEJRKekALav04rdpYDxyNEg8b2",
    ]
    res = api.post_entry(entry, random.choice(photos))
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
            f"Script will download data from {EPG.URL} " "and post entry on Wykop.pl"
        )
    )
    parser.add_argument(
        "--demo",
        help="Entry will be generated, but not published on Wykop.pl",
        action="store_true",
    )
    token = parser.add_argument(
        "--token",
        help="Wykop token. Can be ignored, if --demo is set",
    )

    args = parser.parse_args()
    if not args.demo:
        if args.token is None:
            raise argparse.ArgumentError(token, "Need to be specified")

    return args


def main() -> None:

    movie = Movie("Znachor", datetime.timedelta(hours=2, minutes=8), year=1981)
    args = get_args()
    em = get_emmissions(movie)
    pprint(em)
    future_em = [e for e in em if not e.already_took_place()]
    add_emissions_to_history(em)
    if future_em:
        counter = get_counter(increment=not args.demo)
        msg = Entry(future_em, counter).get_msg()
        print(msg)
        if not args.demo:
            api = get_wykop(args.token)
            add_wykop_entry(api, msg)
            with open("secret.txt", "w") as file:
                file.write(api.connector.refresh_token)
    else:
        print("No future emmissions")


if __name__ == "__main__":
    main()
