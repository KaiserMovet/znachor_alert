import datetime
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
    def __init__(self, title, channel, start, stop):
        self.title = title
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
    def msg(self) -> str:
        return f"{self.channel} -> {self.start_readable} - {self.stop_readable.split()[-1]}"

    def __repr__(self) -> str:
        return f"< Emission {self.title} {self.channel} {self.start} >"


class TVParser:
    def __init__(self, tv: ElementTree.Element):
        self.tv = tv

    def get_all_elements(self, title: str):
        res = self.tv.findall(f".//*[.='{title}']/..")
        emissions: List[Emission] = []
        for re in res:
            em = Emission(
                title=title,
                channel=re.get("channel"),
                start=re.get("start"),
                stop=re.get("stop"),
            )
            if not em.already_took_place():
                emissions.append(em)
        emissions.sort(key=lambda x: x.start)
        return emissions
