import enum


class Currency(enum.Enum):
    """Enum of currencies."""
    RUBLE = 1
    DOLLAR = 2

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Currency) and self.value == __o.value
