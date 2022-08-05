import asyncio
from datetime import datetime

from aiogram.utils.exceptions import ChatNotFound
from apps.feedback.bot.base import BaseBot
from apps.feedback.bot.utils.message import SingleMessage
from apps.feedback.models import NotificationsReceiver
from apps.feedback.service.bot import (build_notification_message,
                                       get_telegram_bot)
from apps.feedback.service.order import (
    get_outdated_orders_without_sent_notifications, mark_orders_as_sent)
from apps.feedback.service.receivers import get_all_receivers
from apps.orders.service.parse.google_sheets_parser import GoogleSheetsParser
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.repositories.currency_repository.exceptions import (
    BadResponseFromCurrencyAPIException, MultipleCurrenciesInResponseException,
    NoSuchCurrencyInResponseException)
from apps.orders.service.repositories.currency_repository.repository import \
    BankOfRussiaCurrencyToRublesRepository
from apps.orders.utils.logger import get_default_logger
from asgiref.sync import sync_to_async
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
        asyncio.get_event_loop().run_until_complete(
            self.send_notifications()
        )

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

    async def send_notifications(self) -> None:
        receivers = await sync_to_async(list)(get_all_receivers())
        bot = get_telegram_bot()
        async with bot as bot_context:
            for person in receivers:
                await self._send_message_to_user(person, bot_context)

    async def _send_message_to_user(
        self,
        receiver: NotificationsReceiver,
        bot: BaseBot
    ) -> None:
        now = datetime.now()
        # Get the QuerySet
        query_set_of_outdated_orders = await sync_to_async(
            get_outdated_orders_without_sent_notifications
        )(receiver.telegram_id, date_=now.date())
        # Evaluate the queryset
        orders_without_notifications = await sync_to_async(list)(
            query_set_of_outdated_orders
        )
        if len(orders_without_notifications) == 0:
            self.logger.info("There are no orders to send...")
            return
        text = build_notification_message(orders_without_notifications)
        await bot.send_message(
            SingleMessage(text),
            user_id=receiver.telegram_id
        )
        try:
            await sync_to_async(mark_orders_as_sent)(
                orders_without_notifications,
                receiver.telegram_id
            )
        except ChatNotFound:
            self.logger.error(
                "ChatNotFound error occurred. " +
                "Are you sure that the user have sent any message to the bot?"
            )


celery_app.register_task(ParseOrdersTask())
