"""a file that allow us to use more specific errors"""

from typing import dict


class CompanyNotFound(Exception):
    """class used when fetching a company from an api"""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> dict:
        return {f"{self.message}, (value: {self.value})"}


class InvalidTickerError(Exception):
    """class used for invalid tickers (length, weird chars)"""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> dict:
        return {f"{self.message}, (value: {self.value})"}


class DataFetchError(Exception):
    """class used when a data fetch operation fails"""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> dict:
        return {f"{self.message}, (value: {self.value})"}
