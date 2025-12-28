"""A module providing specific custom exceptions for the backend."""


class CompanyNotFound(Exception):
    """Exception raised when a company cannot be found via API."""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}, (value: {self.value})"


class InvalidTickerError(Exception):
    """Exception raised for invalid ticker formats (length, characters)."""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}, (value: {self.value})"


class DataFetchError(Exception):
    """Exception raised when a data fetch operation fails."""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}, (value: {self.value})"


class GeminiError(Exception):
    """Exception raised when a gemini fails to generate a response"""

    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}, (value: {self.value})"
