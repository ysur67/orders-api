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
from apps.orders.utils.logger import get_default_logger
from asgiref.sync import sync_to_async
from celery import Task
from project import celery_app


class SendNotificationsTask(Task):
    name = "apps.feedback.tasks.SendNotificationsTask"

    def __init__(self) -> None:
        super().__init__()
        self.logger = get_default_logger("SendNotificationsTask")

    def run(self, *args, **kwargs):
        asyncio.get_event_loop().run_until_complete(
            self.send_notifications()
        )

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


celery_app.register_task(SendNotificationsTask())
