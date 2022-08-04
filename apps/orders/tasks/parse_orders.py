from datetime import datetime
from typing import Any, Optional

from apps.orders.service.parse.google_sheets_parser import GoogleSheetsParser
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.repositories.currency_repository.exceptions import (
    BadResponseFromCurrencyAPIException, MultipleCurrenciesInResponseException,
    NoSuchCurrencyInResponseException)
from apps.orders.service.repositories.currency_repository.repository import \
    BankOfRussiaCurrencyRepository
from apps.orders.utils.logger import get_default_logger
from celery import Task
from django.conf import settings
from project import celery_app


class ParseOrdersTask(Task):

    name = "apps.orders.tasks.ParseOrdersTask"

    def run(self, *args, **kwargs):
        logger = get_default_logger("ParseOrdersTask")
        logger.info("Launching the parser...")
        try:
            repository = BankOfRussiaCurrencyRepository(
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
        except NotImplementedError as not_implemented_error:
            logger.error(
                "Not implemented error occurred. " +
                "Are you sure you used the correct currencies? " +
                "Error message: %s",
                not_implemented_error
            )
        except (
            BadResponseFromCurrencyAPIException,
            MultipleCurrenciesInResponseException,
            NoSuchCurrencyInResponseException,
            AssertionError,
        ) as error:
            logger.error("An error occurred, %s. %s", type(error), error)


celery_app.register_task(ParseOrdersTask())
