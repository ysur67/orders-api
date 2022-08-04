from typing import Optional

from apps.feedback.models import NotificationsReceiver
from django.db.models import QuerySet


def get_all_receivers() -> QuerySet[NotificationsReceiver]:
    return NotificationsReceiver.objects.all()


def get_receiver_by_id(id: int) -> Optional[NotificationsReceiver]:
    try:
        return NotificationsReceiver.objects.get(id=id)
    except NotificationsReceiver.DoesNotExist:
        return None


def get_receiver_by_telegram_id(telegram_id: int) -> Optional[NotificationsReceiver]:
    try:
        return NotificationsReceiver.objects.get(telegram_id=telegram_id)
    except NotificationsReceiver.DoesNotExist:
        return None
