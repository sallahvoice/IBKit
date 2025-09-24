"""
Company domain model.
"""


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
        """
        Initialize a Company instance.

        Args:
            ticker (str): The stock ticker symbol.
            name (str, optional): The company name.
            incorporation (str, optional): Country or state of incorporation.
            sector (str, optional): Industry sector.
            market_cap (int, optional): Market capitalization.
        """
        self.ticker = ticker
        self.name = name
        self.incorporation = incorporation
        self.sector = sector
        self.market_cap = market_cap

    def __repr__(self):
        """
        Return a string representation of the company.
        """
        result = [f"{self.ticker}"]
        if self.name:
            result.append(f"represents {self.name}")
        if self.incorporation:
            result.append(f"which is incorporated in {self.incorporation}")
        if self.sector:
            result.append(f", {self.name} operates in {self.sector} industry")
        if self.market_cap is not None and self.market_cap > 0:
            result.append(f"and has a market cap of {self.market_cap}")
        return " ".join(result)

    def __eq__(self, other) -> bool:
        """
        Check equality based on ticker symbol (case-insensitive).
        """
        if not isinstance(other, Company):
            return False
        return self.ticker.upper() == other.ticker.upper()

    def __hash__(self) -> int:
        """
        Hash based on the uppercased ticker symbol.
        """
        return hash(self.ticker.upper())

    def __lt__(self, other) -> bool:
        """
        Compare companies by ticker symbol (case-insensitive).
        """
        if not isinstance(other, Company):
            return NotImplemented
        return self.ticker.upper() < other.ticker.upper()

    @property
    def display_name(self) -> str:
        """
        Return a display-friendly name for the company.
        """
        if self.name:
            return f"{self.name}. ({self.ticker})"
        return self.ticker

    @property
    def is_complete(self) -> bool:
        """
        Check if all attributes are set (not None or falsy).
        """
        attributes = [
            self.name,
            self.ticker,
            self.incorporation,
            self.sector,
            self.market_cap,
        ]
        return all(attributes)

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

    @classmethod
    def create_company_from_dict(cls, provided_dict: dict) -> "Company":
        """
        Create a Company instance from a dictionary.
        """
        return cls(
            ticker=provided_dict["ticker"],
            name=provided_dict.get("name"),
            incorporation=provided_dict.get("incorporation"),
            sector=provided_dict.get("sector"),
            market_cap=provided_dict.get("market_cap"),
        )

    @classmethod
    def create_company_from_ticker(cls, provided_ticker: str) -> "Company":
        """
        Create a Company instance with only a ticker.
        """
        return cls(ticker=provided_ticker)

    @staticmethod
    def normalize_ticker(ticker) -> str:
        """
        Normalize ticker by stripping whitespace, uppercasing, and removing spaces.
        """
        return ticker.strip().upper().replace(" ", "")

    @staticmethod
    def is_valid_ticker(ticker) -> bool:
        """
        Validate ticker: must be 2-4 alphabetic characters after normalization.
        """
        normalized_ticker = Company.normalize_ticker(
            ticker
        )  # Call static method from class
        return 1 < len(normalized_ticker) < 5 and normalized_ticker.isalpha()

    def to_dict(self) -> dict:
        """Convert company to dictionary."""
        return {
            "ticker": self.ticker,
            "name": self.name,
            "incorporation": self.incorporation,
            "sector": self.sector,
            "market_cap": self.market_cap,
        }
