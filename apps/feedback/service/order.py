from datetime import date
from typing import Iterable

from apps.feedback.models import OrderNotification
from apps.feedback.service.receivers import get_receiver_by_telegram_id
from apps.orders.models import Order
from django.db.models import QuerySet


def get_orders_without_sent_message(receiver_id: int, date: date) -> QuerySet[Order]:
    sent_notifications = OrderNotification.objects.filter(
        receiver__id=receiver_id,
        is_sent=True,
    ).values('order__id')
    return Order.objects.exclude(
        id__in=sent_notifications,
        delivery_date__gt=date
    )


def mark_orders_as_sent(orders: Iterable[Order], user_id: int) -> QuerySet[OrderNotification]:
    receiver = get_receiver_by_telegram_id(user_id)
    if receiver is None:
        return
    values = [OrderNotification(receiver=receiver, order=elem, is_sent=True)
              for elem in orders]
    return OrderNotification.objects.bulk_create(values)
