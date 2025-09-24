from dataclasses import dataclass, asdict
from decimal import Decimal, getcontext
from typing import Optional
from enum import Enum
from analysis.projections import ProjectionResult
# Set decimal precision for financial calculations
getcontext().prec = 10

# Set decimal precision for financial calculations
getcontext().prec = 10

class Stage(Enum):
    GROWTH = "Growth"
    STABLE = "Stable"

Percent = Decimal
Money = int

@dataclass(frozen=True, slots=True, kw_only=True)
class FinancialSnapshot:
    """
    Core financial snapshot - focuses on fundamental value drivers
    """
    # General
    marginal_tax_rate: Decimal
    
    # Income statement attributes
    last_annual_revenue: Money
    last_annual_ebit: Money
    last_annual_net_income: Money
    last_annual_interest_expense: Money
    last_annual_tax_paid: Money
    trailing_sales: Optional[Money] = None#needed for target company only
    trailing_ebit: Optional[Money] = None#needed for target company only

    # Balance sheet attributes
    last_annual_debt: Money
    last_annual_cash : Optional[Money] = None#needed for target company only
    last_annual_equity: Money

    # Cash flow statement attributes
    last_annual_capex: Money
    last_annual_chng_wc: Money
    last_annual_da: Money  # depreciation & amortization

    # Market attributes
    market_cap: Money
    current_shares_outstanding: int
    current_beta: float

    def __post_init__(self):
        """Function validates instance attributes"""
        if self.last_annual_debt < 0:
            raise ValueError("debt must be non-negative")
        if self.book_capital < 0:
            raise ValueError("capital must be non-negative")
        if self.current_shares_outstanding < 0:
            raise ValueError("shares outstanding must be non-negative")
        if not Decimal("0") <= self.marginal_tax_rate <= Decimal("1"):
            raise ValueError("marginal tax must be between 0 and 1")
    
    @propery
    def net_debt(self) -> Optional[Money]:
        if self.last_annual_cash is None:
            return None
        return self.last_annual_debt + self.last_annual_cash

    @property
    def book_capital(self) -> Money:
        """Invested capital (book): Debt + Book Equity."""
        return self.last_annual_debt + self.last_annual_equity

    @property
    def market_capital(self) -> Money:
        """Capital for weighting (market): Debt (book) + Market Cap (equity)."""
        return self.last_annual_debt + self.market_cap

    @property
    def debt_to_equity_market(self) -> Percent:
        """Debt / Equity ratio."""
        if self.market_cap == 0:
            return Decimal("0")
        return Decimal(self.last_annual_debt) / Decimal(self.market_cap)

    @property
    def debt_to_capital_market(self) -> Percent:
        """Debt / capital ratio."""
        if self.market_capital == 0:
            return Decimal("0")
        return Decimal(self.last_annual_debt) / Decimal(self.market_capital)
        
    @property
    def profit_margin(self) -> Percent:
        """Net profit margin"""
        if self.last_annual_revenue == 0:
            return Decimal("0")
        return Decimal(self.last_annual_net_income) / Decimal(self.last_annual_revenue)

    @property
    def ebit_margin(self) -> Percent:
        """EBIT margin"""
        if self.last_annual_revenue == 0:
            return Decimal("0")
        return Decimal(self.last_annual_ebit) / Decimal(self.last_annual_revenue)

    @property
    def nopat(self) -> Money:
        """Net Operating Profit After Tax"""
        return int(Decimal(self.last_annual_ebit) * (Decimal("1") - self.marginal_tax_rate))

    @property
    def roic(self) -> Percent:
        """Return on Invested Capital"""
        if self.book_capital == 0:
            return Decimal("0")
        return Decimal(self.nopat) / Decimal(self.book_capital)

    @property
    def reinvestment_rate(self) -> Percent:
        """Reinvestment Rate = (Capex + Change in WC) / NOPAT"""
        if self.nopat == 0:
            return Decimal("0")
        return Decimal(self.last_annual_capex + self.last_annual_chng_wc) / Decimal(self.nopat)

    @property
    def fcfe_as_percent_net_income(self) -> Percent:
        """FCFE as percentage of Net Income"""
        de = self.debt_to_equity_market
        reinvest = self.last_annual_capex + self.last_annual_chng_wc - self.last_annual_da
        
        if self.last_annual_net_income == 0:
            return Decimal("0")
        
        if de == 0:
            fcfe = self.last_annual_net_income - reinvest
        else:
            debt_financing = de / (Decimal("1") + de) * reinvest
            fcfe = self.last_annual_net_income - reinvest + debt_financing
            
        return Decimal(fcfe) / Decimal(self.last_annual_net_income)

    @property
    def effective_tax_rate(self) -> Percent:
        """Effective tax rate based on actual taxes paid"""
        if self.last_annual_ebit == 0:
            return Decimal("0")
        taxes_paid = self.last_annual_ebit - self.last_annual_net_income - self.last_annual_interest_expense
        return Decimal(taxes_paid) / Decimal(self.last_annual_ebit)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StageParams:
    """Parameters for a specific valuation stage"""
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
    """
    Two-stage growth model parameters
    Stage 1: High growth period
    Stage 2: Stable perpetual growth
    """
    growth: StageParams
    stable: StageParams
    risk_free_rate: Percent
    equity_risk_premium: Percent
    default_spread: Percent
    gdp_growth: Percent  # <-- new field

    def stable_beta(self, raw_beta: float) -> float:
        """Constrain beta for the stable stage between 0.8 and 1.2."""
        return max(0.8, min(1.2, raw_beta))

    def growth_after_tax_ebit(projected: ProjectionResult, snapshot: FinancialSnapshot) -> Percent:
        return average(projected.ebit[:-1])*(1 - snapshot.marginal_tax_rate)/(average(projected.revenues[:-1]))

    def cost_of_equity(self, stage: StageParams, beta: Optional[float] = None) -> Percent:
        """Calculate cost of equity using CAPM."""
        effective_beta = beta if beta is not None else stage.beta
        if stage.stage == Stage.STABLE:
            effective_beta = self.stable_beta(effective_beta)
        return self.risk_free_rate + Decimal(str(effective_beta)) * self.equity_risk_premium

    def cost_of_debt(self, stage: StageParams, snapshot: FinancialSnapshot) -> Percent:
        """Calculate after-tax cost of debt."""
        if stage.stage == Stage.GROWTH and snapshot.last_annual_debt > 0:
            pre_tax_cost = Decimal(snapshot.last_annual_interest_expense) / Decimal(snapshot.last_annual_debt)
            return pre_tax_cost * (Decimal("1") - snapshot.marginal_tax_rate)
        else:
            pre_tax_cost = self.risk_free_rate + self.default_spread
            return pre_tax_cost * (Decimal("1") - snapshot.marginal_tax_rate)

    def wacc(self, stage: StageParams, snapshot: FinancialSnapshot) -> Percent:
        """Calculate Weighted Average Cost of Capital."""
        cost_of_equity = self.cost_of_equity(stage)
        cost_of_debt = self.cost_of_debt(stage, snapshot)

        if stage.stage == Stage.GROWTH:
            d_over_v = snapshot.debt_to_capital_market
        else:
            d_over_v = stage.debt_to_capital_override or snapshot.debt_to_capital_market

        e_over_v = Decimal("1") - d_over_v
        return (cost_of_equity * e_over_v) + (cost_of_debt * d_over_v)

    def growth_rate(self, snapshot: FinancialSnapshot, stage: StageParams) -> Percent:
        """Calculate implied growth rate."""
        if stage.stage == Stage.GROWTH:
            # Growth = ROIC × Reinvestment Rate
            return snapshot.roic * snapshot.reinvestment_rate
        else:
            # Stable growth = min(Risk-free rate, GDP growth) unless overridden
            if stage.growth_rate_override is not None:
                return stage.growth_rate_override
            return min(self.risk_free_rate, self.gdp_growth)

# Utility functions
def de_to_dv(d_over_e: Percent) -> Percent:
    """Convert Debt/Equity to Debt/Value ratio"""
    if d_over_e < 0:
        return Decimal("0")
    return d_over_e / (d_over_e + Decimal("1"))

def dv_to_de(d_over_v: Percent) -> Percent:
    """Convert Debt/Value to Debt/Equity ratio"""
    if not Decimal("0") <= d_over_v <= Decimal("1"):
        return Decimal("0")
    return d_over_v / (Decimal("1") - d_over_v)
