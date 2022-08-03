
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from apps.orders.models import Order
from apps.orders.service.parse.exceptions import CredentialsFileDoesNotExist
from apps.orders.service.repositories.currency_repository.base import \
    BaseCurrencyRepository
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.usecases.order import get_all_orders, get_order_by_id
from apps.orders.utils.file_utils import check_if_file_exist, write_in_file
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
    cost_rubles: float
    delivery_date: date


def map_data_to_row(data: Iterable[Any], rubles_per_dollar: float) -> GoogleSheetRow:
    cost_in_dollars = float(data[2])
    return GoogleSheetRow(
        id=int(data[0]),
        order_id=data[1],
        cost_dollars=cost_in_dollars,
        cost_rubles=cost_in_dollars * rubles_per_dollar,
        delivery_date=datetime.strptime(data[3], '%d.%m.%Y').date()
    )


def map_row_to_model(row: GoogleSheetRow) -> Order:
    return Order(
        id=row.id,
        order_id=row.order_id,
        cost_dollars=row.cost_dollars,
        cost_rubles=row.cost_rubles,
        delivery_date=row.delivery_date,
    )


class GoogleSheetsParser(BaseParser):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = '1bSjKMCN-7roNe0apm1E8Z8gIwbgeo448ekBWvot66zo'
    SAMPLE_RANGE_NAME = 'A2:D'

    def __init__(
        self,
        creds_path: Path,
        token_path: Path,
        repository: BaseCurrencyRepository
    ) -> None:
        super().__init__()
        self.creds_path = creds_path
        self.token_path = token_path
        self.repository = repository
        self.rows: Iterable[GoogleSheetRow] = None
        self.rubles_per_dollar: float = None

    def set_up(self) -> None:
        self._fetch_current_rubles_course()
        self._fetch_rows_from_google_sheets()

    def _fetch_rows_from_google_sheets(self) -> None:
        absolute_token_path = self.token_path.absolute()
        absolute_creds_path = self.creds_path.absolute()
        if not check_if_file_exist(absolute_token_path):
            flow = InstalledAppFlow.from_client_secrets_file(
                absolute_creds_path,
                self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            write_in_file(self.token_path, creds.to_json())
        creds = Credentials.from_authorized_user_file(
            absolute_token_path,
            self.SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
            range=self.SAMPLE_RANGE_NAME
        ).execute()
        self.rows = list(map(
            lambda el: map_data_to_row(el, self.rubles_per_dollar),
            result.get("values", [])
        ))

    def _fetch_current_rubles_course(self) -> None:
        self.rubles_per_dollar = self.repository.get_currency_value()

    def parse(self) -> None:
        required_fields = [self.rows, self.rubles_per_dollar]
        assert all(elem is not None for elem in required_fields), \
            f"Some of required fields, ${required_fields} are None, you must call the set_up method first"
        list(map(self.parse_single_row, self.rows))
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
        order.cost_rubles = row.cost_rubles
        order.delivery_date = row.delivery_date
        order.save()
        return order
