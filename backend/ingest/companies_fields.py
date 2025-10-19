from typing import List


def create_companies_fields(tickers: List[str]) -> List[dict]:
    """
    fetches certain company data (sector, mc..) needed for the Company class
    """
    companies_fields = []
    for ticker in tickers:
        info = ticker.info
        if not info:
            return {"error": "could not get ticker.info for companies tickers"}
        company_field = {
            "ticker": ticker,
            "name": info.get("longName"),
            "incorporation": info.get("incorporation"), #returns None (not provided via yf api)
            "sector": info.get("sector"),
            "market_cap": info.get("marketcap")
        }
        companies_fields.append(company_field)