class NotEmptyDict(dict):
    """
    Subclass of dictionary. None values are ignored.
    """

    def __setitem__(self, key, value) -> None:
        if value is not None:
            super().__setitem__(key, value)
