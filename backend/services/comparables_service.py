from typing import Optional, Dict, List

from ingest.fetch import target_company_filters, screener, create_financial_data
from ingest.companies_fields import create_companies_fields
from ingest.companies_snapshot_fields import create_companies_snapshot_fields
from ingest.stage_params_fields import create_params_for_companies
from ingest.projection_config_fields import create_projection_config

from domain.company import Company
from domain.comparables import ComparableCompany, ComparableSet
from domain.financials.models import FinancialSnapshot, TwoStageGrowthParams
from domain.analysis.projections import (
    CompanyInputsHolder,
    ProjectionResult,
    EquityMultiplesEngine,
    FirmMultiplesEngine,
    build_projections
)

from db.repositories.comparable_repository import ComparableRepository


def analyze_company(ticker: str) -> Dict:
    """
    Analyze a company by fetching its financial data and finding comparable companies.

    Args:
        ticker (str): The stock ticker symbol of the target company.
    
    Returns:
        Dict with analysis results or error message
    """
    
    # Step 1: Get target company filters
    mc, beta = target_company_filters(ticker)
    if not mc or not beta:
        return {"error": "Could not fetch market cap and beta for target company"}
    
    # Step 2: Screen for comparable companies
    comparables = screener(mc, beta)
    if not comparables:
        return {"error": "No comparable companies found"}
    
    # Step 3: Fetch financial data for target + comparables
    all_tickers = [ticker] + comparables
    financial_data = create_financial_data(all_tickers)
    if not financial_data:
        return {"error": "Could not fetch financial data"}
    
    # Step 4: Extract tickers from dataframes (validation)
    tickers = []
    for df in financial_data:
        df_ticker = df.get("ticker")
        if df_ticker:
            tickers.append(df_ticker)
    
    if not tickers:
        return {"error": "Failed to extract tickers from financial data"}
    
    # Step 5: Create Company objects
    companies_fields = create_companies_fields(tickers)
    if not companies_fields:
        return {"error": "Could not fetch company metadata (name, sector, etc.)"}
    
    companies = {}
    for company_fields in companies_fields:
        company = Company.create_company_from_dict(company_fields)
        companies[company.ticker] = company
    
    if not companies:
        return {"error": "Failed to create Company objects"}
    
    # Step 6: Create snapshot fields (dict of dicts)
    snapshot_fields = create_companies_snapshot_fields(financial_data)
    if not snapshot_fields:
        return {"error": "Failed to extract financial snapshot fields"}
    
    # Step 7: Extract betas for creating stage params
    companies_betas = {}
    for ticker, fields in snapshot_fields.items():
        beta_value = fields.get("current_beta")
        if beta_value:
            companies_betas[ticker] = beta_value
    
    if not companies_betas:
        return {"error": "Failed to extract beta values"}
    
    # Step 8: Create TwoStageGrowthParams for each company
    companies_params = create_params_for_companies(companies_betas)
    if not companies_params:
        return {"error": "Failed to create valuation parameters"}
    
    # Step 9: Convert snapshot fields to FinancialSnapshot objects
    financial_snapshots = {}
    for ticker, fields in snapshot_fields.items():
        try:
            financial_snapshots[ticker] = FinancialSnapshot(**fields)
        except Exception as e:
            return {"error": f"Failed to create FinancialSnapshot for {ticker}: {str(e)}"}
    
    
    # Step 10: Prepare CompanyInputsHolder for each company
    #first you need ProjectionConfig -> ProjectionResult objects
    # Create ProjectionConfig (placeholder, implement as needed)
    projection_config = {}
    projected = {}
    inputs = {}
    for ticker in tickers:
        projection_config[ticker] = create_projection_config(two_stage_params=companies_params[ticker])
        projected[ticker] = build_projections(base_revenue=financial_snapshots[ticker],
                                      assumptions=projection_config[ticker],
                                      params=companies_params[ticker],
                                      years=10)
        inputs[ticker] = CompanyInputsHolder.build_attrs(c=companies[ticker],
                                                snapshot=financial_snapshots[ticker],
                                                assumptions=projection_config,
                                                params=companies_params[ticker],
                                                projected=projected[ticker])

    companies_multiples = {}
    for ticker in tickers:
        ticker_inputs = inputs[ticker]
        ticker_params = companies_params[ticker]
        ticker_snapshot = financial_snapshots[ticker]

        equity_engine = EquityMultiplesEngine(params=ticker_inputs,
                                            info=ticker_params)
        
        firm_engine = FirmMultiplesEngine(params=ticker_inputs,
                                        info=ticker_params,
                                        snapshot=ticker_snapshot)
        #equity multiples
        forward_pe = equity_engine.forward_pe(params=ticker_inputs,
                                            info=ticker_params)
        price_to_book = equity_engine.price_to_book(params=ticker_inputs,
                                                info=ticker_params)
        forward_price_to_sales = equity_engine.forward_price_to_sales(params=ticker_inputs,
                                                                info=ticker_params)
        #firm multiples
        forward_ev_over_ebit = firm_engine.forward_ev_over_ebit(params=ticker_inputs,
                                                                snapshot=ticker_snapshot)
        trailing_ev_over_ebit = firm_engine.trailing_ev_over_ebit(params=ticker_inputs,
                                                                snapshot=ticker_snapshot)

        forward_ev_over_sales = firm_engine.forward_ev_over_sales(params=ticker_inputs)

        companies_multiples[ticker] = {
            "forward_pe": forward_pe,
            "price_to_book": price_to_book,
            "forward_price_to_sales": forward_price_to_sales,
            "forward_ev_to_ebit": forward_ev_over_ebit,
            "trailing_ev_to_ebit": trailing_ev_over_ebit,
            "forward_ev_to_sales": forward_ev_over_sales
        }

    comparable_companies = []
    for ticker in tickers:
        multiples = companies_multiples[ticker]
        comparable_company = ComparableCompany(
            ticker=ticker,
            name=companies[ticker].name,
            forward_pe=multiples["forward_pe"],
            price_to_book=multiples["price_to_book"],
            forward_price_to_sales=multiples["forward_price_to_sales"],
            forward_ev_over_ebit=multiples["forward_ev_to_ebit"],
            trailing_ev_to_ebit=multiples["trailing_ev_to_ebit"],
            forward_ev_over_sales=multiples["forward_ev_to_sales"] 
        )
        comparable_companies.append(comparable_company)

    comparable_set = ComparableSet(companies=comparable_companies)

    for comp in comparable_companies:
        