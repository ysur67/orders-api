from rest_framework.generics import ListAPIView

from apps.orders.serializers import OrderSerializer
from apps.orders.service.usecases.order import get_all_orders


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return get_all_orders()
