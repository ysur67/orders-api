
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from apps.orders.models import Order
from apps.orders.service.repositories.currency_repository.base import \
    BaseCurrencyRepository
from apps.orders.service.repositories.currency_repository.currencies import \
    Currency
from apps.orders.service.usecases.order import get_all_orders, get_order_by_id
from apps.orders.utils.convert_utils import (str_to_date, str_to_float,
                                             str_to_int)
from apps.orders.utils.file_utils import check_if_file_exist, write_in_file
from apps.orders.utils.logger import get_default_logger
from apps.orders.utils.reset_pks import reset_autoincrement_fields
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .base import BaseParser


@dataclass
class GoogleSheetRow:
    """Typed data from Google Sheet's row"""
    id: int
    order_id: str
    cost_dollars: float
    cost_rubles: float
    delivery_date: date


class GoogleSheetsParser(BaseParser):
    """Order parser from Google Sheets"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = '1bSjKMCN-7roNe0apm1E8Z8gIwbgeo448ekBWvot66zo'
    SAMPLE_RANGE_NAME = 'A:D'

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
        self.logger = get_default_logger("GoogleSheetsParser")
        self.rows: Iterable[GoogleSheetRow] = None
        self.rubles_per_dollar: float = None
        assert self.repository.currency == Currency.DOLLAR, \
            "The repository class should receive a number of rubles only " + \
            "for a dollar. In the context of Google Sheets Parser"

    def set_up(self) -> None:
        self._fetch_current_rubles_course()
        self._fetch_rows_from_google_sheets()

    def _fetch_current_rubles_course(self) -> None:
        """Get the number of rubles per dollar"""
        self.rubles_per_dollar = round(
            self.repository.get_amount_of_rubles_per_currency(),
            2
        )
        self.logger.info(
            "Got %s rubles for currency %s, from %s",
            self.rubles_per_dollar,
            self.repository.currency,
            type(self.repository)
        )

    def _fetch_rows_from_google_sheets(self) -> None:
        absolute_token_path = self.token_path.absolute()
        absolute_creds_path = self.creds_path.absolute()
        self.logger.info("Got absolute token path %s", absolute_token_path)
        self.logger.info("Got absolute creds path %s", absolute_creds_path)
        if not check_if_file_exist(absolute_creds_path):
            raise FileNotFoundError(
                f"Couldn't find the creds file by path: {absolute_creds_path}"
            )
        if not check_if_file_exist(absolute_token_path):
            self.logger.warning(
                "There is no token.json file by path %s",
                absolute_token_path
            )
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
        self.rows = []
        for elem in result.get("values", []):
            row = map_data_to_row(elem, self.rubles_per_dollar)
            if row is not None:
                self.rows.append(row)

    def parse(self) -> None:
        required_fields = [self.rows, self.rubles_per_dollar]
        assert all(elem is not None for elem in required_fields), \
            f"Some of required fields, ${required_fields} are None, " + \
            "you must call the set_up method first"
        list(map(self._parse_single_row, self.rows))
        row_ids = tuple(map(lambda item: item.id, self.rows))
        # remove orders that are not presented in current data
        orders = get_all_orders().exclude(id__in=row_ids)
        orders_count = orders.count()
        rows_deleted, _ = orders.delete()
        self.logger.warning(
            "Deletion of %s orders affected %s rows in DB",
            orders_count,
            rows_deleted
        )
        # reset autoincrement fields to prevent IntegrityErrors from psql.
        reset_autoincrement_fields([Order])

    def _parse_single_row(self, row: GoogleSheetRow) -> Order:
        order = get_order_by_id(row.id)
        return self._create_order(row) if order is None else self._update_order(order, row)

    def _create_order(self, row: GoogleSheetRow) -> Order:
        self.logger.info("Creating order from row: %s", row)
        result = map_row_to_model(row)
        result.save()
        return result

    def _update_order(self, order: Order, row: GoogleSheetRow) -> Order:
        self.logger.info("Updating order from row: %s", row)
        order.order_id = row.order_id
        order.cost_dollars = row.cost_dollars
        order.cost_rubles = row.cost_rubles
        order.delivery_date = row.delivery_date
        order.save()
        return order


def map_data_to_row(data: Iterable[Any], rubles_per_dollar: float) -> GoogleSheetRow:
    """Map google sheets data to row

    Args:
        data (Iterable[Any]): Data
        rubles_per_dollar (float): rubles per one dollar

    Returns:
        GoogleSheetRow
    """
    if len(data) == 0:
        return None
    id_ = str_to_int(data[0])
    order_id = data[1]
    cost_in_dollars = str_to_float(data[2])
    delivery_date = str_to_date(data[3])
    if any(elem is None for elem in [id_, order_id, cost_in_dollars, delivery_date]):
        return None
    return GoogleSheetRow(
        id=id_,
        order_id=order_id,
        cost_dollars=cost_in_dollars,
        cost_rubles=round(cost_in_dollars * rubles_per_dollar, 2),
        delivery_date=delivery_date
    )


def map_row_to_model(row: GoogleSheetRow) -> Order:
    """Map GoogleSheetRow to Order object

    Args:
        row (GoogleSheetRow): Data from Google Sheet

    Returns:
        Order: Order object
    """
    return Order(
        id=row.id,
        order_id=row.order_id,
        cost_dollars=row.cost_dollars,
        cost_rubles=row.cost_rubles,
        delivery_date=row.delivery_date,
    )
