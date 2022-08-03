from datetime import datetime
from typing import Iterable

import requests
from lxml import etree

from .base import BaseCurrencyRepository
from .currencies import Currency
from .exceptions import (BadResponseFromCurrencyAPIException,
                         MultipleCurrenciesInResponseException,
                         NoSuchCurrencyInResponseException)


class BankOfRussiaCurrencyRepository(BaseCurrencyRepository):
    """The Bank of Russia repository for receiving the ruble exchange rate
    relative to currencies.
    """

    SUPPORTED_CURRENCIES = [
        Currency.DOLLAR,
    ]

    def __init__(
        self,
        currency: Currency,
        url: str,
        date: datetime,
    ) -> None:
        super().__init__(currency)
        self.url = url
        self.date = date
        if self.currency not in self.SUPPORTED_CURRENCIES:
            raise NotImplementedError(
                f"There is no implementation for currency: {self.currency.name}"
            )

    def get_amount_of_rubles_per_currency(self) -> float:
        response = requests.get(
            self.url,
            params={"date_req": self.date.strftime("%d/%m/%Y")}
        )
        if not response.status_code == 200:
            raise BadResponseFromCurrencyAPIException()
        currency_code = currency_to_bank_of_russia_code(self.currency)
        return self._get_value_from_response_by_code(response.text, currency_code)

    def _get_value_from_response_by_code(self, xml_body: str, currency_code: str) -> float:
        root: etree._Element = etree.fromstring(
            bytes(xml_body, encoding="windows-1251")
        )
        # Get all valute elements from root elem
        valute_elements: Iterable[etree._Element] = root.findall("Valute")
        # Find the valute by code
        single_valute_element = tuple(filter(
            lambda el: el.get("ID") == currency_code,
            valute_elements
        ))
        # If there are no elements in collection, raise exception
        if len(single_valute_element) == 0:
            raise NoSuchCurrencyInResponseException(
                f"There is no currency: {currency_code} in response"
            )
        # If there are more, than one element in collection, raise exception
        if len(single_valute_element) > 1:
            raise MultipleCurrenciesInResponseException(
                f"There are more than one currency: {currency_code} in response"
            )
        # Take the only element from collection
        single_valute_element: etree._Element = single_valute_element[0]
        # Take it's value and then parse it to a float type
        value_element: etree._Element = single_valute_element.find("Value")
        string_value = value_element.text
        return float(string_value.replace(",", "."))


def currency_to_bank_of_russia_code(currency: Currency) -> str:
    """Get the currency code from the Bank of Russia by Currency enum.

    Args:
        currency (Currency): Selected currency

    Raises:
        NotImplementedError: If there is no code for such currency

    Returns:
        str: The code of currency
    """
    if currency == Currency.DOLLAR:
        return "R01235"
    raise NotImplementedError(
        f"There is no implementation for currency: {currency.name}"
    )
