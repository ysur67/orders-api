

from abc import ABC, abstractmethod


class BaseCurrencyRepository(ABC):

    @abstractmethod
    def get_currency_value(self) -> float:
        pass
