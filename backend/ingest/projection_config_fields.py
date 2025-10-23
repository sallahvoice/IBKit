from domain.analysis.projections import ProjectionConfig
from domain.financials.models import TwoStageGrowthParams
from decimal import Decimal

# Default stable year assumptions
DEFAULT_STABLE_EBIT_MARGIN = 0.20
DEFAULT_STABLE_CAPEX_PCT = 0.07
DEFAULT_STABLE_WC_CHANGE_PCT = 0.01
DEFAULT_STABLE_DA_PCT = 0.05
DEFAULT_STABLE_NET_INCOME_MARGIN = 0.10


def create_projection_config(
    two_stage_params: TwoStageGrowthParams,
    stable_ebit_margin: float = DEFAULT_STABLE_EBIT_MARGIN,
    stable_capex_pct: float = DEFAULT_STABLE_CAPEX_PCT,
    stable_wc_change_pct: float = DEFAULT_STABLE_WC_CHANGE_PCT,
    stable_da_pct: float = DEFAULT_STABLE_DA_PCT,
    stable_net_income_margin: float = DEFAULT_STABLE_NET_INCOME_MARGIN
) -> ProjectionConfig:
    """
    Create ProjectionConfig with stable year assumptions.
    Stable year revenue growth comes from TwoStageGrowthParams.
    """
    # Get stable growth rate from params (will use GDP growth or override)
    stable_growth = two_stage_params.growth_rate(
        snapshot=None,  # Not needed for stable stage with override
        stage=two_stage_params.stable
    )
    
    return ProjectionConfig(
        stable_year_revenue_growth=float(stable_growth),
        stable_year_ebit_percent_revenue=stable_ebit_margin,
        stable_year_capex_percent_revenue=stable_capex_pct,
        stable_year_chng_wc_percent_revenue=stable_wc_change_pct,
        stable_year_da_percent_revenue=stable_da_pct,
        stable_year_net_income_percent_revenue=stable_net_income_margin
    )