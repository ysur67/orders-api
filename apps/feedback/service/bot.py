from typing import Iterable

from apps.feedback.bot.telegram_bot import TelegramBot
from apps.feedback.utils.date import to_message_format
from apps.orders.models import Order
from django.conf import settings


def get_telegram_bot() -> TelegramBot:
    return TelegramBot(settings.TELEGRAM_TOKEN)


def build_notification_message(orders: Iterable[Order]) -> str:
    """Get notification message for orders."""
    return "\n====\n".join([build_single_order_message(elem) for elem in orders])


def build_single_order_message(order: Order) -> str:
    """Get notification message for one order."""
    return f"У заказа #{order.order_id} " + \
        f"истекает дата доставки {to_message_format(order.delivery_date)}."
