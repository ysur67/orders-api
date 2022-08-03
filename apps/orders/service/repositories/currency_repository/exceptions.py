

class BadResponseFromCurrencyAPIException(Exception):
    pass


class NoSuchCurrencyInResponseException(Exception):
    pass


class MultipleCurrenciesInResponseException(Exception):
    pass
