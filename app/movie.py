from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, eq=True)
class Movie:
    title: str
    length: timedelta
