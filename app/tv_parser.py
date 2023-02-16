import datetime
import hashlib
from functools import cache
from typing import List
from xml.etree import ElementTree

import pytz

from .movie import Movie


class Translate:
    weekdays = {
        "Monday": "Poniedziałek",
        "Tuesday": "Wtorek",
        "Wednesday": "Środa",
        "Thursday": "Czwartek",
        "Friday": "Piątek",
        "Saturday": "Sobota",
        "Sunday": "Niedziela",
    }
    months = {
        "January": "stycznia",
        "February": "lutego",
        "March": "marca",
        "April": "kwietnia",
        "May": "maja",
        "June": "czerwca",
        "July": "lipca",
        "August": "sierpnia",
        "September": "września",
        "October": "października",
        "November": "listopada",
        "December": "grudnia",
    }

    @classmethod
    def weekday(cls, weekday: str) -> str:
        return cls.weekdays.get(weekday, weekday)

    @classmethod
    def month(cls, month: str) -> str:
        return cls.months.get(month, month)


class Emission:
    def __init__(
        self,
        movie: Movie,
        channel: str,
        start: str,
        stop: str,
    ) -> None:
        self.movie = movie
        self.channel = channel
        self.start = datetime.datetime.strptime(start, "%Y%m%d%H%M%S %z")
        self.stop = datetime.datetime.strptime(stop, "%Y%m%d%H%M%S %z")

    @staticmethod
    def _get_readable_date(date) -> str:
        poland_tz = pytz.timezone("Europe/Warsaw")
        dt_poland = date.astimezone(poland_tz)
        month_name = Translate.month(dt_poland.strftime("%B"))
        result = dt_poland.strftime(f"%d {month_name} %H:%M")
        result = f"{Translate.weekday(dt_poland.strftime('%A'))}, {result}"
        return result

    def already_took_place(self) -> bool:
        poland_tz = pytz.timezone("Europe/Warsaw")
        return self.stop < datetime.datetime.now(poland_tz)

    @property
    def start_readable(self) -> str:
        return self._get_readable_date(self.start)

    @property
    def stop_readable(self) -> str:
        return self._get_readable_date(self.stop)

    @property
    def advert_len(self) -> datetime.timedelta | None:
        return (self.stop - self.start) - self.movie.length

    @property
    def msg(self) -> str:
        """
        Generate message.
        If advert len in less than 15 minutes or greater than 120 minuts,
        advert message will not be shown.

        Returns:
            str: msg
        """
        msg = (
            f"{self.channel} -> {self.start_readable} - "
            f"{self.stop_readable.split()[-1]}"
        )
        advert_len = self.advert_len
        if (
            advert_len
            and advert_len > datetime.timedelta(minutes=15)
            and advert_len <= datetime.timedelta(minutes=120)
        ):
            # Remove 15 minutes
            advert_len = advert_len - datetime.timedelta(minutes=15)
            msg += f" ({((advert_len).total_seconds() // 60):.0f} min reklam)"
        return msg

    def __repr__(self) -> str:
        return f"< Emission {self.movie.title} {self.channel} {self.start} >"

    def __hash__(self) -> int:
        return int(
            hashlib.md5(
                (f"{self.movie.title} {self.channel} {self.start}").encode()
            ).hexdigest(),
            16,
        )

    def to_dict(self) -> dict:
        return {
            "title": self.movie.title,
            "channel": self.channel,
            "start": self.start.timestamp(),
            "stop": self.stop.timestamp(),
            "id": hash(self),
        }


class TVParser:
    def __init__(self, tv: ElementTree.Element) -> None:
        self.tv = tv

    @cache  # pylint: disable=method-cache-max-size-none
    def get_all_elements(self, movie: Movie) -> list[Emission]:
        res = self.tv.findall(f".//*[.='{movie.title}']/..")
        emissions: List[Emission] = []
        for re in res:
            year = None
            try:
                year = int(re.find(".//date").text)  # type: ignore
            except Exception:  # pylint: disable=broad-except
                pass
            if year != movie.year:
                continue
            em = Emission(
                movie=movie,
                channel=re.get("channel"),  # type: ignore
                start=re.get("start"),  # type: ignore
                stop=re.get("stop"),  # type: ignore
            )
            emissions.append(em)
        emissions.sort(key=lambda x: x.start)
        return emissions
