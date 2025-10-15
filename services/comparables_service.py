from typing import Optional, Dict, List
from ingest.fetch import target_company_filters, screener, fetch_financial_data
from domain.company import Company
from domain.comparables import ComparableCompany, ComparableSet
from domain.financials.models import FinancialSnapshot, TwoStageGrowthParams
from domain.analysis.projections import EquityMultiplesEngine, FirmMultiplesEngine


def analyze_company(ticker: str) -> Dict:
    """
    Analyze a company by fetching its financial data and finding comparable companies.

    Args:
        ticker (str): The stock ticker symbol of the target company.
    """

    filter = target_company_filters(ticker)
    if not filter:
        return {"error": "No filter found for the given ticker."}
    
    comparables = screener(filter)
    if not comparables:
        return {"error": "No comparable companies found."}
    
    financial_data = fetch_financial_data([ticker] + comparables)
    if not financial_data:
        return {"error": "could not fetch financial data."}
    
