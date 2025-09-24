from dataclasses import dataclass, fields, asdict
from typing import Tuple, List, Optional, Any
from statistics import mean, median

Money = int
Multiple = float

@dataclass(frozen=True, slots=True)
class ComparableCompany:
    """
    Represents a single comparable company for multiples analysis.
    Stores fundamental drivers and valuation multiples.
    """
    ticker: str
    name: str
    forward_price_to_book: Multiple
    forward_pe: Multiple
    trailing_pe: Multiple
    forward_price_to_sale: Multiple
    trailing_ev_to_ebit: Multiple
    trailing_ev_to_sales: Multiple

    def multiples_tuple(self) -> Tuple[Multiple, ...]:
        """
        Returns a tuple of all Multiple-typed fields.
        """
        return tuple(getattr(self, f.name) for f in fields(self) if f.type is Multiple)

    def all_tuple(self) -> Tuple[Any, ...]:
        """
        Returns a tuple of all fields.
        """
        return tuple(getattr(self, f.name) for f in fields(self))

    def as_dict(self) -> dict:
        """
        Returns a dictionary representation of the company.
        """
        return asdict(self)

@dataclass
class ComparableSet:
    """
    Represents a set of comparable companies for analysis.
    """
    companies: List[ComparableCompany]

    def add(self, company: ComparableCompany) -> None:
        """
        Adds a company to the set.
        """
        self.companies.append(company)

    def remove(self, ticker: str) -> None:
        """
        Removes a company by ticker.
        """
        self.companies = [c for c in self.companies if c.ticker != ticker]

    def get(self, ticker: str) -> Optional[ComparableCompany]:
        """
        Retrieves a company by ticker.
        """
        return next((c for c in self.companies if c.ticker == ticker), None)

    def average_multiple(self, attr: str, lower: Multiple = 0, upper: Multiple = 60) -> Multiple:
        """
        Returns the mean of a multiple attribute within bounds.
        """
        values = [getattr(c, attr) for c in self.companies if lower < getattr(c, attr) < upper]
        return mean(values) if values else float("nan")

    def median_multiple(self, attr: str, lower: Multiple = 0, upper: Multiple = 60) -> Multiple:
        """
        Returns the median of a multiple attribute within bounds.
        """
        values = [getattr(c, attr) for c in self.companies if lower < getattr(c, attr) < upper]
        return median(values) if values else float("nan")

    def top(self, attr: str, n: Optional[int] = None) -> List[ComparableCompany]:
        """
        Returns the top n companies sorted by a given attribute.
        """
        n = n or len(self.companies)
        return sorted(self.companies, key=lambda c: getattr(c, attr), reverse=True)[:n]

    def bottom(self, attr: str, n: Optional[int] = None) -> List[ComparableCompany]:
        """
        Returns the bottom n companies sorted by a given attribute.
        """
        n = n or len(self.companies)
        return sorted(self.companies, key=lambda c: getattr(c, attr))[:n]

    def tickers(self) -> List[str]:
        """
        Returns a list of all company tickers.
        """
        return [c.ticker for c in self.companies]

    def companies_as_dict_list(self) -> List[dict]:
        """
        Returns a list of company dictionaries.
        """
        return [c.as_dict() for c in self.companies]

    def summary(self, attr: str, lower: Multiple = 0, upper: Multiple = 60) -> dict:
        """
        Returns summary statistics for a given attribute.
        """
        values = [getattr(c, attr) for c in self.companies if lower < getattr(c, attr) < upper]
        return {
            "min": min(values, default=None),
            "max": max(values, default=None),
            "mean": mean(values) if values else None,
            "median": median(values) if values else None
        }