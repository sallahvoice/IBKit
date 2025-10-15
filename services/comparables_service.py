from typing import Optional, Dict, List
from ingest.fetch import target_company_filters, screener, fetch_financial_data
from domain.company import Company
from domain.comparables import ComparableCompany, ComparableSet
from domain.financials.models import FinancialSnapshot, TwoStageGrowthParams
from domain.analysis.projections import (CompanyInputsHolder,ProjectionResult,
EquityMultiplesEngine, FirmMultiplesEngine)
from db.repositories.comparable_repository import ComparableRepository


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
    
    tickers = []
    for df in financial_data:
        ticker = df.get("ticker")
        tickers.append(ticker)

    companies_fields = fetch_companies_fields(tickers) #add it to ingest.fetch (ticker, name, incorporation, sector, mc)
    
    if not companies_fields:
        return {"error": "could not fetch comparable companies data fields"}
    
    companies = []
    for company_fields in companies_fields:
        company = Company(company_fields)
        companies.append(company)

    if not companies:
        return {"error": "failed to create company objects"}

    
    #ComparableCompany & ComparableSet are the last classes you interact with
