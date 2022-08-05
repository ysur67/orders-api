from datetime import datetime
from typing import Any, Optional

from apps.orders.service.parse.google_sheets_parser import GoogleSheetsParser
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.repositories.currency_repository.repository import \
    BankOfRussiaCurrencyToRublesRepository
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        repository = BankOfRussiaCurrencyToRublesRepository(
            currency=Currency.DOLLAR,
            url="https://www.cbr.ru/scripts/XML_daily.asp",
            date=datetime.now(),
        )
        parser = GoogleSheetsParser(
            creds_path=settings.BASE_DIR / 'credentials.json',
            token_path=settings.BASE_DIR / 'token.json',
            repository=repository,
        )
        parser.set_up()
        parser.parse()
