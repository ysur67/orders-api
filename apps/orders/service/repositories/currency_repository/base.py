from abc import ABC, abstractmethod

from apps.orders.service.repositories.currency_repository.currencies import \
    Currency


class BaseCurrencyRepository(ABC):

    def __init__(self, from_currency: Currency, target_currency: Currency) -> None:
        self.from_currency = from_currency
        self.target_currency = target_currency

    @abstractmethod
    def get_currency_value(self) -> float:
        pass
