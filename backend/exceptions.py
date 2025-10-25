from typing import Any

class CompanyNotFound(Exception):
    def __init__(self, message: str, value: str) -> None:
        super.__init__(message)
        self.message = message
        self.value = value
    
    def __str__(self) -> str:
        return {f"{self.message}, (value: {self.value})"}
    
class InvalidTickerError(Exception):
    def __init__(self, message: str, value: str) -> None:
        super.__init__(message)
        self.message = message
        self.value = value
    
    def __str__(self) -> str:
        return {f"{self.message}, (value: {self.value})"}
    
class DataFetchError(Exception):
    def __init__(self, message: str, value: str) -> None:
        super.__init__(message)
        self.message = message
        self.value = value
    
    def __str__(self) -> str:
        return {f"{self.message}, (value: {self.value})"}
