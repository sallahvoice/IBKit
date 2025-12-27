"""file that contains Company class with its attributes & dunder methodes (__repr__, __hash--) & other property function for validation ..."""

from typing import Dict


class Company:
    """
    Represents a company with financial and business attributes.
    """

    def __init__(
        self,
        ticker: str,
        name: str | None = None,
        incorporation: str | None = None,
        sector: str | None = None,
        market_cap: int | None = None,
    ):
        """Initialize a Company instance."""
        self.ticker = ticker.strip().upper().replace(" ", "")
        self.name = name
        self.incorporation = incorporation
        self.sector = sector
        self.market_cap = market_cap

    def __repr__(self):
        """Return a string representation of the company."""
        result = [f"{self.ticker}"]
        if self.name:
            result.append(f"represents {self.name}")
        if self.incorporation:
            result.append(f"which is incorporated in {self.incorporation}")
        if self.sector:
            result.append(f", {self.name} operates in the {self.sector} industry")
        if self.market_cap is not None and self.market_cap > 0:
            result.append(f"and has a market cap of {self.market_cap}")
        return " ".join(result)

    def __eq__(self, other) -> bool:
        """Check equality based on ticker symbol (case-insensitive)."""
        if not isinstance(other, Company):
            return False
        return self.ticker == other.ticker.upper()

    def __hash__(self) -> int:
        """Hash based on ticker symbol."""
        return hash(self.ticker)

    def __lt__(self, other) -> bool:
        """Compare companies by ticker symbol (case-insensitive)."""
        if not isinstance(other, Company):
            return NotImplemented
        return self.ticker < other.ticker.upper()

    @property
    def display_name(self) -> str:
        """Return a display-friendly name for the company."""
        if self.name:
            return f"{self.name}, ({self.ticker})"
        return self.ticker

    @property
    def is_complete(self) -> bool:
        """Check if all attributes are set (not None or falsy)."""
        return all(
            [
                self.name,
                self.ticker,
                self.incorporation,
                self.sector,
                self.market_cap,
            ]
        )

    @property
    def market_cap_category(self) -> str:
        """Categorize company by market cap size."""
        if not self.market_cap:
            return "Unknown"
        elif self.market_cap >= 200_000_000_000:
            return "Mega Cap"
        elif self.market_cap >= 10_000_000_000:
            return "Large Cap"
        elif self.market_cap >= 2_000_000_000:
            return "Mid Cap"
        elif self.market_cap >= 300_000_000:
            return "Small Cap"
        else:
            return "Micro Cap"

    def is_valid_ticker(self) -> bool:
        """Validate ticker: must be 2–4 alphabetic characters."""
        return 1 < len(self.ticker) < 5 and self.ticker.isalpha()

    @classmethod
    def create_company_from_dict(cls, provided_dict: dict) -> "Company":
        """Create a Company instance from a dictionary."""
        return cls(
            ticker=provided_dict["ticker"],
            name=provided_dict.get("name"),
            incorporation=provided_dict.get("incorporation"),
            sector=provided_dict.get("sector"),
            market_cap=provided_dict.get("market_cap"),
        )

    @classmethod
    def create_company_from_ticker(cls, provided_ticker: str) -> "Company":
        """Create a Company instance with only a ticker."""
        return cls(ticker=provided_ticker)

    def to_dict(self) -> dict:
        """Convert company to dictionary."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "incorporation": self.incorporation,
            "sector": self.sector,
            "market_cap": self.market_cap,
        }

    @classmethod
    def from_db_record(cls, record: Dict) -> "Company":
        """Convert database record to a company object."""
        return cls(
            ticker=record["ticker"],
            name=record["name"],
            incorporation=record["incorporation"],
            sector=record["sector"],
            market_cap=record["market_cap"],
        )

    def to_db_dict(self) -> dict:
        """Convert company to dictionary for database insertion."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "incorporation": self.incorporation,
            "sector": self.sector,
            "market_cap": self.market_cap,
        }
