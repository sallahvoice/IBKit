"""file that sets assumptions, creates stage params, growth stage params then two stage params for a company..."""

from decimal import Decimal
from typing import Dict, Optional

from backend.domain.financials.models import Stage, StageParams, TwoStageGrowthParams

# Default market assumptions (will make these configurable later)
DEFAULT_RISK_FREE_RATE = Decimal("0.04")  # 4%
DEFAULT_EQUITY_RISK_PREMIUM = Decimal("0.06")  # 6%
DEFAULT_DEFAULT_SPREAD = Decimal("0.015")  # 1.5%
DEFAULT_GDP_GROWTH = Decimal("0.025")  # 2.5%

# Default stage assumptions
DEFAULT_GROWTH_YEARS = 5
DEFAULT_STABLE_YEARS = 1  # Terminal year (always 1)


def create_growth_stage_params(
    beta: float,
    years: int = DEFAULT_GROWTH_YEARS,
    growth_rate_override: Optional[Decimal] = None,
    debt_to_capital_override: Optional[Decimal] = None,
) -> StageParams:
    """
    Create growth stage parameters.

    Args:
        beta: Company's beta for growth stage
        years: Number of high growth years (default 5)
        growth_rate_override: Optional override for calculated growth rate
        debt_to_capital_override: Optional override for debt/capital ratio
    """
    return StageParams(
        stage=Stage.GROWTH,
        years=years,
        beta=beta,
        growth_rate_override=growth_rate_override,
        debt_to_capital_override=debt_to_capital_override,
    )


def create_stable_stage_params(
    beta: float,
    growth_rate_override: Optional[Decimal] = None,
    debt_to_capital_override: Optional[Decimal] = None,
) -> StageParams:
    """
    Create stable stage parameters.

    Args:
        beta: Company's beta (will be constrained to 0.8-1.2)
        growth_rate_override: Optional override for stable growth
        debt_to_capital_override: Optional override for stable D/V ratio
    """
    return StageParams(
        stage=Stage.STABLE,
        years=DEFAULT_STABLE_YEARS,  # Always 1 for terminal year
        beta=beta,
        growth_rate_override=growth_rate_override,
        debt_to_capital_override=debt_to_capital_override,
    )


def create_two_stage_growth_params(
    growth_stage: StageParams,
    stable_stage: StageParams,
    risk_free_rate: Decimal = DEFAULT_RISK_FREE_RATE,
    equity_risk_premium: Decimal = DEFAULT_EQUITY_RISK_PREMIUM,
    default_spread: Decimal = DEFAULT_DEFAULT_SPREAD,
    gdp_growth: Decimal = DEFAULT_GDP_GROWTH,
) -> TwoStageGrowthParams:
    """
    Create two-stage growth model parameters.

    Args:
        growth_stage: Growth stage parameters
        stable_stage: Stable stage parameters
        risk_free_rate: Risk-free rate (default 4%)
        equity_risk_premium: Equity risk premium (default 6%)
        default_spread: Default spread for debt (default 1.5%)
        gdp_growth: Expected GDP growth (default 2.5%)
    """
    return TwoStageGrowthParams(
        growth=growth_stage,
        stable=stable_stage,
        risk_free_rate=risk_free_rate,
        equity_risk_premium=equity_risk_premium,
        default_spread=default_spread,
        gdp_growth=gdp_growth,
    )


def create_default_params_for_company(beta: float) -> TwoStageGrowthParams:
    """
    Convenience function to create default parameters for a company.
    Uses standard assumptions for all parameters.

    Args:
        beta: Company's current beta

    Returns:
        TwoStageGrowthParams with default assumptions
    """
    growth_stage = create_growth_stage_params(beta=beta)
    stable_stage = create_stable_stage_params(beta=beta)

    return create_two_stage_growth_params(
        growth_stage=growth_stage, stable_stage=stable_stage
    )


def create_params_for_companies(
    companies_betas: Dict[str, float],
) -> Dict[str, TwoStageGrowthParams]:
    """
    Create default parameters for multiple companies.

    Args:
        companies_betas: Dict mapping ticker -> beta

    Returns:
        Dict mapping ticker -> TwoStageGrowthParams
    """
    params = {}
    for ticker, beta in companies_betas.items():
        params[ticker] = create_default_params_for_company(beta)

    return params
