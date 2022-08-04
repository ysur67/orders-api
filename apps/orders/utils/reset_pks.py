from typing import Iterable

from apps.orders.models import Order
from django.core.management.color import no_style
from django.db import connection
from django.db.models import Model


def reset_autoincrement_fields(models: Iterable[Model]) -> None:
    """Reset the autoincrement fields in psql.

    i.e. id
    """
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
