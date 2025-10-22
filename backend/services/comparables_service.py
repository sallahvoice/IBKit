from typing import Optional, Dict, List
from ingest.fetch import (target_company_filters, screener,
                          create_financial_data)
from ingest.companies_fields import create_companies_fields
from ingest.companies_snapshot_fields import create_companies_snapshot_fields
from domain.company import Company
from domain.financials.models import Stage
from domain.comparables import ComparableCompany, ComparableSet
from domain.financials.models import FinancialSnapshot, TwoStageGrowthParams
from domain.analysis.projections import (CompanyInputsHolder,ProjectionResult,
                                         EquityMultiplesEngine, FirmMultiplesEngine)
from db.repositories.comparable_repository import ComparableRepository


#add try except for better handling
def analyze_company(ticker: str) -> Dict:
    """
    Analyze a company by fetching its financial data and finding comparable companies.

    Args:
        ticker (str): The stock ticker symbol of the target company.
    """

    mc, beta = target_company_filters(ticker)
    if not mc or not beta:
        return {"error": "No filter found for the given ticker."}
    
    comparables = screener(mc, beta)
    if not comparables:
        return {"error": "No comparable companies found."}
    
    financial_data = create_financial_data([ticker] + comparables)
    if not financial_data:
        return {"error": "could not fetch financial data."}
    
    tickers = []
    for df in financial_data:
        ticker = df.get("ticker")
        tickers.append(ticker)

    if not tickers:
        return {"error": "failed to grab tickers from dataframes"}
    
    for ticker in tickers: #this is okay for now but when facing stage & twosatageparams make sure you make it dynamic (different projection length across companies)
        return Stage("growth", "stable")


    companies_fields = create_companies_fields(tickers) #add it to ingest.fetch (ticker, name, incorporation, sector, mc)
    
    if not companies_fields:
        return {"error": "could not fetch comparable companies data fields"}
    
    companies = []
    for company_fields in companies_fields:
        company = Company.create_company_from_dict(company_fields)
        companies.append(company)

    if not companies:
        return {"error": "failed to create companies objects"}


    companies_financial_snapshot_fields = create_companies_snapshot_fields(financial_data)
    if not companies_financial_snapshot_fields :
        return {"error": "failed to fetch companies snapshot fields"}
    else:
        companies_snapshots = [] #do we need this
        for company_fields in companies_financial_snapshot_fields: 
            company_snapshot = FinancialSnapshot(company_fields)
            companies_snapshots.append(company_snapshot)

    if not companies_snapshots:
        return {"error": "failed to create companies snapshot objects"}
    
    companies_stages = {}
    for ticker in tickers:
        company_stages = Stage("Growth", "Stable")
        companies[ticker]["stage"] = company_stages

    if not companies_stages:
        return {"error": "failed to create stage objects for tickers"}
    
    #next: StageParams & TwoStageParams

    
    #ComparableCompany & ComparableSet are the last classes you interact with
