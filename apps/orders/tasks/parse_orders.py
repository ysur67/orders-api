from datetime import datetime

from apps.feedback.tasks.send_notifications_task import SendNotificationsTask
from apps.orders.service.parse.google_sheets_parser import GoogleSheetsParser
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.repositories.currency_repository.exceptions import (
    BadResponseFromCurrencyAPIException, MultipleCurrenciesInResponseException,
    NoSuchCurrencyInResponseException)
from apps.orders.service.repositories.currency_repository.repository import \
    BankOfRussiaCurrencyToRublesRepository
from apps.orders.utils.logger import get_default_logger
from celery import Task
from django.conf import settings
from httplib2.error import ServerNotFoundError
from project import celery_app
from requests.exceptions import ConnectionError


class ParseOrdersTask(Task):

    name = "apps.orders.tasks.ParseOrdersTask"

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_default_logger("ParseOrdersTask")

    def run(self, *args, **kwargs):
        self.run_parser()
        send_notifications_task = SendNotificationsTask()
        send_notifications_task.delay()

    def run_parser(self) -> None:
        self.logger.info("Launching the parser...")
        try:
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
        except (ConnectionError, ServerNotFoundError) as connection_error:
            self.logger.error(
                "Connection error occurred: %s",
                connection_error
            )
        except FileNotFoundError as file_not_found_error:
            self.logger.error(str(file_not_found_error))
        except NotImplementedError as not_implemented_error:
            self.logger.error(
                "Not implemented error occurred. " +
                "Are you sure you used the correct currencies? " +
                "Error message: %s", not_implemented_error
            )
        except (
            BadResponseFromCurrencyAPIException,
            MultipleCurrenciesInResponseException,
            NoSuchCurrencyInResponseException,
            AssertionError,
        ) as error:
            self.logger.error("An error occurred, %s. %s", type(error), error)


celery_app.register_task(ParseOrdersTask())
