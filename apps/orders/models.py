from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    order_id = models.CharField(verbose_name=_("Ид заказа"), max_length=200,)
    cost_dollars = models.FloatField(verbose_name=_("Стоимость в долларах"),)
    cost_rubles = models.FloatField(verbose_name=_("Стоимость в рублях"))
    delivery_date = models.DateField(verbose_name=_("Дата доставки"))

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self) -> str:
        return f"Заказ #{self.order_id}"
