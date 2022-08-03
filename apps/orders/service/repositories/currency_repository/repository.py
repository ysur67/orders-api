from datetime import datetime
from typing import Iterable

import requests
from lxml import etree

from .base import BaseCurrencyRepository
from .currencies import Currency
from .exceptions import (BadResponseFromCurrencyAPIException,
                         MultipleCurrenciesInResponseException,
                         NoSuchCurrencyInResponseException)


class BankOfRussiaCurrencyRepository(
    BaseCurrencyRepository,
):
    SUPPORTED_FROM_CURRENCIES = [
        Currency.DOLLAR,
    ]

    def __init__(
        self,
        from_currency: Currency,
        target_currency: Currency,
        url: str,
        date: datetime,
    ) -> None:
        super().__init__(from_currency, target_currency)
        self.url = url
        self.date = date
        if self.from_currency not in self.SUPPORTED_FROM_CURRENCIES:
            raise NotImplementedError(
                f"There is no implementation for currency: {self.from_currency.name}"
            )

    def get_currency_value(self) -> float:
        response = requests.get(
            self.url,
            params={"date_req": self.date.strftime("%d/%m/%Y")}
        )
        if not response.status_code == 200:
            raise BadResponseFromCurrencyAPIException()
        currency_code = currency_to_bank_of_russia_code(self.from_currency)
        return self._get_value_from_response_by_code(response.text, currency_code)

    def _get_value_from_response_by_code(self, xml_body: str, currency_code: str) -> float:
        root: etree._Element = etree.fromstring(
            bytes(xml_body, encoding="windows-1251")
        )
        valute_elements: Iterable[etree._Element] = root.findall('Valute')
        single_valute_element = list(filter(
            lambda el: el.get("ID") == currency_code,
            valute_elements
        ))
        if len(single_valute_element) == 0:
            raise NoSuchCurrencyInResponseException(
                f"There is no currency: {currency_code} in response"
            )
        if len(single_valute_element) > 1:
            raise MultipleCurrenciesInResponseException(
                f"There are more than one currency: {currency_code} in response"
            )
        single_valute_element: etree._Element = single_valute_element[0]
        value_element: etree._Element = single_valute_element.find("Value")
        string_value = value_element.text
        return float(string_value.replace(",", "."))


def currency_to_bank_of_russia_code(currency: Currency) -> str:
    if currency == Currency.DOLLAR:
        return "R01235"
    raise NotImplementedError(
        f"There is no implementation for currency: {currency.name}"
    )
