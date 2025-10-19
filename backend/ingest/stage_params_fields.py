""" class StageParams:
    #Parameters for a specific valuation stage
    stage: Stage
    years: int
    beta: float
    growth_rate_override: Optional[Percent] = None
    debt_to_capital_override: Optional[Percent] = None

    def __post_init__(self):
        if self.stage == Stage.STABLE and self.years != 1:
            raise ValueError("Stable stage must have exactly 1 year (terminal year)")
        if self.debt_to_capital_override is not None and self.debt_to_capital_override < Decimal("0"):
            raise ValueError("debt to capital ratio cannot be negative")


@dataclass(frozen=True, slots=True)
class TwoStageGrowthParams:
    
    #Two-stage growth model parameters
    Stage 1: High growth period
    Stage 2: Stable perpetual growth
    
    growth: StageParams
    stable: StageParams
    risk_free_rate: Percent
    equity_risk_premium: Percent
    default_spread: Percent
    gdp_growth: Percent  # <-- new field
"""

def create_stage_params_fields(companies_stages, companies_financial_snapshot_fields):
    pass    
