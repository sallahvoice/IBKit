from typing import Dict

from backend.domain.analysis.projections import (
    CompanyInputsHolder,
    EquityMultiplesEngine,
    FirmMultiplesEngine,
    build_projections,
)
from backend.domain.company import Company
from backend.domain.comparables import ComparableCompany, ComparableSet
from backend.domain.financials.models import FinancialSnapshot
from backend.ingest.companies_fields import create_companies_fields
from backend.ingest.companies_snapshot_fields import create_companies_snapshot_fields
from backend.ingest.fetch import create_financial_data, screener, target_company_filters
from backend.ingest.projection_config_fields import create_projection_config
from backend.ingest.stage_params_fields import create_params_for_companies
from db.repositories.company_repository import CompanyRepository
from db.repositories.comparable_repository import ComparableRepository
from db.repositories.snapshot_repository import SnapshotRepository


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
    target_ticker = ticker
    peer_tickers = comparables
    all_tickers = [target_ticker] + peer_tickers

    financial_data = create_financial_data(all_tickers)
    if not financial_data:
        return {"error": "Could not fetch financial data"}

    # Step 4: Extract tickers from dataframes (validation)
    tickers = all_tickers

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
    for ticker_key, fields in snapshot_fields.items():
        beta_value = fields.get("current_beta")
        if beta_value:
            companies_betas[ticker_key] = beta_value

    if not companies_betas:
        return {"error": "Failed to extract beta values"}

    # Step 8: Create TwoStageGrowthParams for each company
    companies_params = create_params_for_companies(companies_betas)
    if not companies_params:
        return {"error": "Failed to create valuation parameters"}

    # Step 9: Convert snapshot fields to FinancialSnapshot objects
    financial_snapshots = {}
    for ticker_key, fields in snapshot_fields.items():
        try:
            financial_snapshots[ticker_key] = FinancialSnapshot(**fields)
        except Exception as e:
            return {
                "error": f"Failed to create FinancialSnapshot for {ticker_key}: {str(e)}"
            }

    # Step 10: Create CompanyInputsHolder for each company
    projection_configs = {}
    projections = {}
    inputs = {}

    for ticker_key in tickers:
        projection_configs[ticker_key] = create_projection_config(
            two_stage_params=companies_params[ticker_key]
        )
        projections[ticker_key] = build_projections(
            base_revenue=financial_snapshots[ticker_key],
            assumptions=projection_configs[ticker_key],
            params=companies_params[ticker_key],
            years=5,
        )
        inputs[ticker_key] = CompanyInputsHolder.build_attrs(
            c=companies[ticker_key],
            snapshot=financial_snapshots[ticker_key],
            assumptions=projection_configs[ticker_key],
            params=companies_params[ticker_key],
            projected=projections[ticker_key],
        )

    # Step 11: Compute multiples for each company
    companies_multiples = {}

    for ticker_key in tickers:
        ticker_inputs = inputs[ticker_key]
        ticker_params = companies_params[ticker_key]
        ticker_snapshot = financial_snapshots[ticker_key]

        try:
            # Equity multiples
            forward_pe = EquityMultiplesEngine.forward_pe(ticker_inputs, ticker_params)
            price_to_book = EquityMultiplesEngine.price_to_book(
                ticker_inputs, ticker_params
            )
            forward_price_to_sales = EquityMultiplesEngine.forward_price_to_sales(
                ticker_inputs, ticker_params
            )

            # Trailing PE
            trailing_pe = forward_pe * (1 + ticker_inputs.first_stage_growth)

            # Firm multiples
            trailing_ev_to_ebit = FirmMultiplesEngine.trailing_ev_over_ebit(
                ticker_snapshot, ticker_inputs
            )
            trailing_ev_to_sales = FirmMultiplesEngine.trailing_ev_over_sales(
                ticker_inputs
            )

            companies_multiples[ticker_key] = {
                "forward_pe": forward_pe,
                "forward_price_to_book": price_to_book,
                "forward_price_to_sales": forward_price_to_sales,
                "trailing_pe": trailing_pe,
                "trailing_ev_to_ebit": trailing_ev_to_ebit,
                "trailing_ev_to_sales": trailing_ev_to_sales,
            }
        except Exception as e:
            print(f"Warning: Failed to compute multiples for {ticker_key}: {str(e)}")
            continue

    # Step 12: Build ComparableCompany objects
    comparable_companies = []

    for ticker_key in peer_tickers:
        if ticker_key not in companies_multiples:
            continue

        multiples = companies_multiples[ticker_key]
        comparable_company = ComparableCompany(
            ticker=ticker_key,
            name=companies[ticker_key].name,
            forward_pe=multiples["forward_pe"],
            forward_price_to_book=multiples["forward_price_to_book"],
            forward_price_to_sales=multiples["forward_price_to_sales"],
            trailing_pe=multiples["trailing_pe"],
            trailing_ev_to_ebit=multiples["trailing_ev_to_ebit"],
            trailing_ev_to_sales=multiples["trailing_ev_to_sales"],
        )
        comparable_companies.append(comparable_company)

    # Step 13: Create ComparableSet
    comparable_set = ComparableSet(companies=comparable_companies)

    # Step 14: Save to database
    company_repo = CompanyRepository()
    for company in companies.values():
        company_db_format = company.to_db_dict()
        company_repo.create_company(company_data=company_db_format)

    snapshot_repo = SnapshotRepository()
    for snapshot in financial_snapshots.values():
        snapshot_db_format = snapshot.to_db_dict()
        snapshot_repo.create_snapshot(snapshot_data=snapshot_db_format)

    comparables_repo = ComparableRepository()
    for comparable in comparable_companies:
        comparable_db_format = comparable.to_db_dict()
        comparables_repo.create_comparable(comp_data=comparable_db_format)

    # Step 15: Return results, we might exclude it but for now multiple average methods apply lower & upper bounds for edge cases
    return {
        "success": True,
        "target_ticker": ticker,
        "comparable_count": len(comparable_companies),
        "comparables": [comp.ticker for comp in comparable_companies],
        "summary_stats": {
            "avg_forward_pe": comparable_set.average_multiple("forward_pe"),
            "median_forward_pe": comparable_set.median_multiple("forward_pe"),
            "avg_trailing_ev_to_ebit": comparable_set.average_multiple(
                "trailing_ev_to_ebit"
            ),
            "median_trailing_ev_to_ebit": comparable_set.median_multiple(
                "trailing_ev_to_ebit"
            ),
        },
    }
