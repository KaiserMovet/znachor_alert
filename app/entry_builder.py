import datetime
import random
from typing import List

from .tv_parser import Emission


class Entry:
    def __init__(
        self, emissions: List[Emission], counter: int, rand: int | None = None
    ) -> None:
        self.emissions = emissions
        self.counter = counter
        self.rand = rand or random.randint(0, 100)

    def _RAZY(self) -> str:  # pylint: disable=invalid-name
        amount = len(self.emissions)
        if amount == 1:
            return "1 raz"
        return f"{amount} razy"

    @property
    def _header(self) -> str:
        return f"=== ZNACHOR ALERT!!! {self.counter}/∞ ===\n"

    @property
    def _footer(self) -> str:
        return (
            "\n===\n"
            "Jestem Botem przypominającym o emisjach Znachora w ciągu "
            "najbliższych 5 dni. Wpis będzie tworzony w co 4 dzień każdego "
            "miesiąca (1, 5, 9 itd.), jeśli odbywa się jakaś emisja.\n"
            "Jeśli coś nie działa jak powinno "
            "(zła godzina, coś zostało pominięte, etc.) "
            "dawajcie znać w komentarzach albo pw. Dzięki\n"
            "https://github.com/KaiserMovet/znachor_alert\n"
            # "#znachor #znachoralert" # TODO remove this
        )

    @property
    def _dates_str(self) -> str:
        dates_str = ""
        now = datetime.datetime.now()
        dates_str = (
            f"{now.strftime('%d.%m')} - "
            f"{(now+datetime.timedelta(days=4)).strftime('%d.%m')}"
        )
        return dates_str

    @property
    def _body(self) -> str:
        inner_msg = random.choice(
            [
                "Twój stary dowie się, że to jest profesor Rafał Wilczór",
                "Sonia zostanie odrzucona",
                "Leszek wyjebie się na motorze",
                "Kosiba połamie Norkowi nogi",
                "Norek zatańczy dla czterdziestolatka",
                "rodzice Leszka wezmą go na poważną rozmowę",
                "Wilczór zapali fajkę po operacji",
                "Kosiba zajuma narzędzia lekarzowi",
                "żona zostawi Wilczura",
                "Wilczór pójdzie w srogi melanż",
                "Kosiba powie, że od bab wszelkie zło na świecie",
            ]
        )
        entry = ""

        if not self.emissions:
            entry += (
                f"W ciągu najbliższych 5 dni ({self._dates_str}) "
                "nie odbędzie się żadna emisja Znachora :c\n"
            )
        else:
            entry += (
                f"W ciągu najbliższych 5 dni ({self._dates_str}) "
                f"{inner_msg} {self._RAZY()}:\n"
            )
            entry += "\n".join([em.msg for em in self.emissions])
            entry += "\n"
        return entry

    def get_msg(self) -> str:
        return self._header + self._body + self._footer
