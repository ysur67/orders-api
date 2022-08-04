from django.db import models

from apps.orders.models import Order


class NotificationsReceiver(models.Model):
    """Model of notifications receiver."""

    telegram_id = models.CharField(
        verbose_name="ИД из telegram'а",
        max_length=300,
    )
    name = models.CharField(
        verbose_name="Имя пользователя",
        null=True, blank=True,
        max_length=300,
    )

    class Meta:
        verbose_name = "Получатель сообщений"
        verbose_name_plural = "Получатели сообщений"

    def __str__(self) -> str:
        return f"Получатель сообщений #{self.id}"


class OrderNotification(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ"
    )
    receiver = models.ForeignKey(
        NotificationsReceiver,
        on_delete=models.CASCADE,
        verbose_name="Получатель сообщения"
    )
    is_sent = models.BooleanField(
        verbose_name="Уведомление отправлено?",
        default=False,
    )

    class Meta:
        verbose_name = "Уведомление о заказе"
        verbose_name_plural = "Уведомления о заказах"

    def __str__(self) -> str:
        return f"Уведомление по заказу #{self.id}"
