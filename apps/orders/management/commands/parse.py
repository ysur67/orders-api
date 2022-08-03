from datetime import datetime
from typing import Any, Optional

from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.repositories.currency_repository.repository import \
    BankOfRussiaCurrencyRepository
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        repository = BankOfRussiaCurrencyRepository(
            url="https://www.cbr.ru/scripts/XML_daily.asp",
            date=datetime.now(),
            from_currency=Currency.DOLLAR,
            target_currency=Currency.RUBLE,
        )
        value = repository.get_currency_value()
        print(value)
