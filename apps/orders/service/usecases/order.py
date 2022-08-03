from typing import Optional

from apps.orders.models import Order
from django.db.models import QuerySet


def get_order_by_id(id_: int) -> Optional[Order]:
    try:
        return Order.objects.get(id=id_)
    except Order.DoesNotExist:
        return None


def get_all_orders() -> QuerySet[Order]:
    return Order.objects.all()
