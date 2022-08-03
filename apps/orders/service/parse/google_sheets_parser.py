
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from apps.orders.models import Order
from apps.orders.service.parse.exceptions import CredentialsFileDoesNotExist
from apps.orders.service.usecases.order import get_all_orders, get_order_by_id
from apps.orders.utils.file_utils import check_if_file_exist
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from pyparsing import delimited_list
from requests import delete

from .base import BaseParser


@dataclass
class GoogleSheetRow:
    id: int
    order_id: str
    cost_dollars: float
    delivery_date: date


def map_data_to_row(data: Iterable[Any]) -> GoogleSheetRow:
    return GoogleSheetRow(
        id=int(data[0]),
        order_id=data[1],
        cost_dollars=float(data[2]),
        delivery_date=datetime.strptime('%d.%M.%Y', data[3]).date()
    )


def map_row_to_model(row: GoogleSheetRow) -> Order:
    return Order(
        id=row.id,
        order_id=row.order_id,
        cost_dollars=row.cost_dollars,
        delivery_date=row.delivery_date,
    )


class GoogleSheetsParser(BaseParser):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    SAMPLE_RANGE_NAME = 'Class Data!A2:E'

    def __init__(self, creds_path: Path,) -> None:
        super().__init__()
        self.creds_path = creds_path
        self.rows: Iterable[GoogleSheetRow]
        self.rubles_per_dollar: float

    def set_up(self) -> None:
        self._fetch_rows_from_google_sheets()
        self._fetch_current_rubles_course()

    def _fetch_rows_from_google_sheets(self) -> None:
        absolute_creds_path = self.creds_path.absolute()
        if not check_if_file_exist(absolute_creds_path):
            raise CredentialsFileDoesNotExist(
                f"Credentials path: ${absolute_creds_path} doesn't exist"
            )
        creds = Credentials.from_authorized_user_file(
            absolute_creds_path,
            self.SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
            range=self.SAMPLE_RANGE_NAME
        ).execute()
        self.rows = map(map_data_to_row, result.get("values", []))

    def _fetch_current_rubles_course(self) -> None:
        return

    def parse(self) -> None:
        required_fields = [self.rows, self.rubles_per_dollar]
        assert all(elem is not None for elem in required_fields), \
            f"Some of required fields, ${required_fields} are None, you must call the set_up method first"
        map(self.parse_single_row, self.rows)
        row_ids = list(map(lambda item: item.id, self.rows))
        orders = get_all_orders().exclude(id__in=row_ids)
        orders.delete()

    def parse_single_row(self, row: GoogleSheetRow) -> Order:
        order = get_order_by_id(row.id)
        return self.create_order(row) if order is None else self.update_order(order, row)

    def create_order(self, row: GoogleSheetRow) -> Order:
        result = map_row_to_model(row)
        result.save()
        return result

    def update_order(self, order: Order, row: GoogleSheetRow) -> Order:
        order.order_id = row.order_id
        order.cost_dollars = row.cost_dollars
        order.delivery_date = row.delivery_date
        order.save()
        return order
