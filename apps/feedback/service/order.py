from datetime import date
from typing import Iterable

from apps.feedback.models import OrderNotification
from apps.feedback.service.receivers import get_receiver_by_telegram_id
from apps.orders.models import Order
from django.db.models import QuerySet


def get_orders_without_sent_message(receiver_telegram_id: int, date_: date) -> QuerySet[Order]:
    qs = Order.objects.filter(
        delivery_date__lte=date_
    )
    sent_notifications = OrderNotification.objects.filter(
        receiver__telegram_id__iexact=receiver_telegram_id,
        is_sent=True,
    ).values_list("id", flat=True)
    if sent_notifications.count() != 0:
        qs = qs.exclude(notifications__id__in=sent_notifications)
    return qs


def mark_orders_as_sent(orders: Iterable[Order], telegram_id: int) -> QuerySet[OrderNotification]:
    receiver = get_receiver_by_telegram_id(telegram_id)
    if receiver is None:
        return
    existing_records: QuerySet[OrderNotification] = OrderNotification.objects.filter(
        order__in=orders,
        receiver=receiver,
    )
    for elem in existing_records:
        elem.is_sent = True
    OrderNotification.objects.bulk_update(existing_records, ["is_sent"])
    orders_to_create = [OrderNotification(
        order=el, receiver=receiver, is_sent=True) for el in orders if el not in existing_records]
    return OrderNotification.objects.bulk_create(orders_to_create)
