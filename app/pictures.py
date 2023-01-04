import random


class Pictures:
    AMOUNT = 5
    PATH = "pictures"

    @classmethod
    def get_picture(cls):
        index = random.randint(1, cls.AMOUNT)
        return open(f"{cls.PATH}/{index}.jpg", "rb")
