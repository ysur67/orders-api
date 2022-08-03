from abc import ABC, abstractmethod

from apps.orders.service.repositories.currency_repository.currencies import \
    Currency


class BaseCurrencyRepository(ABC):
    """Abstract class for receiving the ruble exchange rate
    relative to currencies.
    """

    def __init__(self, currency: Currency) -> None:
        self.currency = currency

    @abstractmethod
    def get_amount_of_rubles_per_currency(self) -> float:
        """Get number of rubles for one conventional currency unit

        Returns:
            float: Number of rubles for one conventional currency unit
        """
