import datetime
import hashlib
from functools import cache
from typing import List
from xml.etree import ElementTree

import pytz


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
    def __init__(self, title, channel, start, stop, default_timedelta=None):
        self.title = title
        self.channel = channel
        self.start = datetime.datetime.strptime(start, "%Y%m%d%H%M%S %z")
        self.stop = datetime.datetime.strptime(stop, "%Y%m%d%H%M%S %z")
        self.timedelta = default_timedelta

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
        if self.timedelta:
            return (self.stop - self.start) - self.timedelta
        return None

    @property
    def msg(self) -> str:
        msg = f"{self.channel} -> {self.start_readable} - {self.stop_readable.split()[-1]}"
        td = self.advert_len
        if td and td > datetime.timedelta(minutes=15):
            # Remove 15 minutes
            td = td - datetime.timedelta(minutes=15)
            msg += f" (min {((td).total_seconds() // 60):.0f} minut reklam)"
        return msg

    def __repr__(self) -> str:
        return f"< Emission {self.title} {self.channel} {self.start} >"

    def __hash__(self) -> int:
        return int(
            hashlib.md5(
                (f"{self.title} {self.channel} {self.start}").encode()
            ).hexdigest(),
            16,
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "channel": self.channel,
            "start": self.start.timestamp(),
            "stop": self.stop.timestamp(),
            "id": hash(self),
        }


class TVParser:
    def __init__(self, tv: ElementTree.Element):
        self.tv = tv

    @cache
    def get_all_elements(self, title: str) -> list[Emission]:
        res = self.tv.findall(f".//*[.='{title}']/..")
        emissions: List[Emission] = []
        for re in res:
            em = Emission(
                title=title,
                channel=re.get("channel"),
                start=re.get("start"),
                stop=re.get("stop"),
                default_timedelta=datetime.timedelta(hours=2, minutes=8),
            )
            emissions.append(em)
        emissions.sort(key=lambda x: x.start)
        return emissions
