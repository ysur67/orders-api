from django.contrib import admin

from apps.feedback.models import NotificationsReceiver, OrderNotification


@admin.register(NotificationsReceiver)
class NotificationsReceiverAdmin(admin.ModelAdmin):
    list_display = ["id", "telegram_id"]


@admin.register(OrderNotification)
class OrderNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "is_sent"]
