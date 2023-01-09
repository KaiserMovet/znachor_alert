import os
import random
from io import BufferedReader
from typing import List


class Pictures:
    PATH = "pictures"

    @classmethod
    def get_files(cls) -> List[str]:
        return [path for path in os.listdir(cls.PATH) if path.endswith(".jpg")]

    @classmethod
    def get_picture(cls) -> BufferedReader:
        picture_path = random.choice(cls.get_files())
        return open(f"{picture_path}", "rb")
