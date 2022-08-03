from typing import Optional

from apps.orders.models import Order
from django.db.models import QuerySet


def get_order_by_id(id_: int) -> Optional[Order]:
    """Get Order object by id.

    Args:
        id_ (int): Unique id of Order object

    Returns:
        Optional[Order]: Order object, if exist, else None
    """
    try:
        return Order.objects.get(id=id_)
    except Order.DoesNotExist:
        return None


def get_all_orders() -> QuerySet[Order]:
    """Get all orders

    Returns:
        QuerySet[Order]: QuerySet of Order objects
    """
    return Order.objects.all()
