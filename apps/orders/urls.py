from django.urls import path

from apps.orders.views import OrderListView

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="orders-list")
]
