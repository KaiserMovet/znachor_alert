import datetime
import os
from xml.etree import ElementTree

import requests


class EPG:

    URL = "https://epg.ovh/plar.xml"

    def __init__(self) -> None:
        self._tree: ElementTree.Element | None = None

    @property
    def tree(self) -> ElementTree.Element:
        if self._tree is None:
            self._tree = self._load_data()
        return self._tree

    def _load_data(self) -> ElementTree.Element:
        today = datetime.datetime.today().strftime("%d.%m.%Y")
        file_name = f"{today}.data.xml"
        self._download_data_if_needed(file_name)
        return self._get_data(file_name)

    @classmethod
    def _download_data_if_needed(cls, file_name: str) -> None:
        if not os.path.exists(file_name):
            resposne = requests.get(cls.URL)
            with open(file_name, "wb") as f:
                f.write(resposne.content)

    @staticmethod
    def _get_data(file_name) -> ElementTree.Element:
        with open(file_name, "rb") as xml_file:
            tree = ElementTree.fromstring(xml_file.read())
        return tree
