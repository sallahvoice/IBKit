from dataclasses import dataclass, replace, asdict
from typing import Union, List
from domain.company import Company
from domain.financials.models import FinancialSnapshot, StageParams, TwoStageGrowthParams
from utils.converge import project_revenue, project_other_line_items, converge_growth

Percent = float
Money = Union[float, int]
Multiple = float

@dataclass(frozen=True, slots=True)
class ProjectionConfig:
    """
    Configuration for projecting financial line items as percentages of revenue.
    """
    stable_year_revenue_growth: Percent
    stable_year_ebit_percent_revenue: Percent = 0.20
    stable_year_capex_percent_revenue: Percent = 0.07
    stable_year_chng_wc_percent_revenue: Percent = 0.01
    stable_year_da_percent_revenue: Percent = 0.05
    stable_year_net_income_percent_revenue: Percent = 0.10

    @classmethod
    def from_growth_params(
        cls,
        params: TwoStageGrowthParams,
        **overrides
    ) -> "ProjectionConfig":
        """
        Create a ProjectionConfig from growth parameters,
        allowing selective overrides for other assumptions.
        """
        base = cls(stable_year_revenue_growth=params.growth_rate)
        normalized_dict = {k: (v / 100 if isinstance(v, int) else v) for k, v in overrides.items()}
        return replace(base, **normalized_dict)

    def __post_init__(self) -> None:
        """
        Validate that all percentage values are within reasonable bounds.
        """
        if not 0.0 < self.stable_year_ebit_percent_revenue < 1.0:
            raise ValueError("EBIT % of revenue must be between 0 and 1")
        if not 0.0 <= self.stable_year_capex_percent_revenue < 1.0:
            raise ValueError("Capex % of revenue must be >= 0 and < 1")
        if not 0.0 <= self.stable_year_chng_wc_percent_revenue < 1.0:
            raise ValueError("Change in WC % of revenue must be >= 0 and < 1")
        if not 0.0 < self.stable_year_da_percent_revenue < 1.0:
            raise ValueError("D&A % of revenue must be > 0 and < 1")
        if not 0.0 < self.stable_year_net_income_percent_revenue < 1.0:
            raise ValueError("Net income % of revenue must be between 0 and 1")

    def as_percentage(self) -> dict:
        """
        Return the configuration as a dictionary of percentages.
        """
        return {k: (v / 100 if isinstance(v, int) else v) for k, v in asdict(self).items()}


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectionResult:
    """
    Holds the projected financial line items for each year.
    """
    revenues: List[Money]
    ebit: List[Money]
    capex: List[Money]
    wc: List[Money]
    da: List[Money]
    net_income: List[Money]

def build_projections(
    base_revenue: FinancialSnapshot,
    assumptions: ProjectionConfig,
    params,
    years: int
) -> ProjectionResult:
    """
    Build financial projections for a given number of years using provided assumptions.
    """
    growths = converge_growth(
        params.growth_rate,
        assumptions.stable_year_revenue_growth,
        years
    )
    revenues = project_revenue(base_revenue.last_annual_revenue, growths)
    ebit = project_other_line_items(revenues, assumptions.stable_year_ebit_percent_revenue)
    capex = project_other_line_items(revenues, assumptions.stable_year_capex_percent_revenue)
    wc = project_other_line_items(revenues, assumptions.stable_year_chng_wc_percent_revenue)
    da = project_other_line_items(revenues, assumptions.stable_year_da_percent_revenue)
    net_income = project_other_line_items(revenues, assumptions.stable_year_net_income_percent_revenue)

    return ProjectionResult(
        revenues=revenues,
        ebit=ebit,
        capex=capex,
        wc=wc,
        da=da,
        net_income=net_income
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompanyInputsHolder:
    # --- Company identifiers ---
    ticker: str
    name: str
    years: int
    shares: int

    # --- Growth assumptions ---
    first_stage_growth: Percent
    second_stage_growth: Percent

    # --- FCFE assumptions (as % of revenue) ---
    growth_stage_fcfe_percent_rev: Percent
    stable_stage_fcfe_percent_rev: Percent

    # --- Discount rate components ---
    growth_stage_risk_free_rate: Percent
    stable_stage_risk_free_rate: Percent
    growth_stage_equity_risk_premium: Percent
    stable_stage_equity_risk_premium: Percent
    growth_stage_beta: Percent
    stable_stage_beta: Percent

    # --- Profitability assumptions ---
    growth_stage_profit_margin: Percent
    stable_stage_profit_margin: Percent

    # --- Cost of capital ---
    growth_stage_wacc: Percent
    stable_stage_wacc: Percent

    # --- Reinvestment ---
    growth_stage_reinvestment_rate: Percent
    stable_stage_reinvestment_rate: Percent

    # --- Forward-looking earnings ---
    expected_next_year_net_income_per_share: Money
    # --- forward-looking-firm-multiples ---
    expected_next_year_after_tax_ebit_per_share: Money

    @classmethod
def build_attrs(
    cls,
    c: "Company",
    snapshot: "FinancialSnapshot",
    assumptions: "ProjectionConfig",
    params: "TwoStageGrowthParams",
    projected: "ProjectionResult",
) -> "CompanyInputsHolder":
    
    # Pre-calculate growth rates
    first_stage_growth = params.growth_rate(snapshot, params.growth)
    second_stage_growth = params.growth_rate(snapshot, params.stable)
    
    # Pre-calculate costs of capital
    growth_wacc = params.wacc(params.growth, snapshot)
    stable_wacc = params.wacc(params.stable, snapshot)
    growth_cost_of_equity = params.cost_of_equity(params.growth)
    stable_cost_of_equity = params.cost_of_equity(params.stable)
    
    # Calculate after-tax EBIT margin for growth stage
    avg_ebit = sum(projected.ebit[:-1]) / len(projected.ebit[:-1])
    avg_revenue = sum(projected.revenues[:-1]) / len(projected.revenues[:-1])
    growth_after_tax_ebit_margin = (
        avg_ebit * (1 - snapshot.marginal_tax_rate) / avg_revenue
    )
    
    # Calculate FCFE as % of revenue (approximation)
    fcfe_pct_net_income = snapshot.fcfe_as_percent_net_income
    growth_fcfe_pct_rev = fcfe_pct_net_income * snapshot.profit_margin
    
    return cls(
        # --- identifiers ---
        ticker=c.ticker,
        name=c.name,
        years=params.growth.years,
        shares=snapshot.current_shares_outstanding,

        # --- growth assumptions ---
        first_stage_growth=float(first_stage_growth),
        second_stage_growth=float(second_stage_growth),

        # --- fcfe assumptions ---
        growth_stage_fcfe_percent_rev=float(growth_fcfe_pct_rev),
        stable_stage_fcfe_percent_rev=assumptions.stable_year_net_income_percent_revenue,

        # --- discount rate components ---
        growth_stage_risk_free_rate=float(params.risk_free_rate),
        stable_stage_risk_free_rate=float(params.risk_free_rate),
        growth_stage_equity_risk_premium=float(params.equity_risk_premium),
        stable_stage_equity_risk_premium=float(params.equity_risk_premium),
        growth_stage_beta=params.growth.beta,
        stable_stage_beta=params.stable.beta,

        # --- profitability assumptions ---
        growth_stage_profit_margin=float(snapshot.profit_margin),
        stable_stage_profit_margin=assumptions.stable_year_net_income_percent_revenue,
        
        # --- after-tax EBIT margin ---
        growth_stage_after_tax_ebit_margin=float(growth_after_tax_ebit_margin),

        # --- cost of capital ---
        growth_stage_wacc=float(growth_wacc),
        stable_stage_wacc=float(stable_wacc),
        growth_stage_cost_of_equity=float(growth_cost_of_equity),
        stable_stage_cost_of_equity=float(stable_cost_of_equity),

        # --- reinvestment ---
        growth_stage_reinvestment_rate=float(snapshot.reinvestment_rate),
        stable_stage_reinvestment_rate=float(snapshot.reinvestment_rate),

        # --- forward EPS ---
        expected_next_year_net_income_per_share=(
            projected.net_income[1] / snapshot.current_shares_outstanding
        ),
        expected_next_year_after_tax_ebit_per_share=(
            projected.ebit[1] * (1 - snapshot.marginal_tax_rate) / 
            snapshot.current_shares_outstanding
        )
    )

@dataclass(frozen=True, slots=True)
class EquityMultiplesEngine:
    """
    Utility class for computing equity multiples using CompanyInputsHolder.
    All methods are stateless and require params to be passed in.
    """

    @staticmethod
    def growth_expected_roe(params: CompanyInputsHolder) -> Percent:
        return params.growth_stage_profit_margin / (1 - params.growth_stage_fcfe_percent_rev)

    @staticmethod
    def stable_expected_roe(params: CompanyInputsHolder) -> Percent:
        return params.stable_stage_profit_margin / (1 - params.stable_stage_fcfe_percent_rev)

    @staticmethod
    def book_value_of_equity(params: CompanyInputsHolder) -> Money:  # per share
        return params.expected_next_year_net_income_per_share / params.first_stage_growth

    @staticmethod
    def expected_revenues_next_year(params: CompanyInputsHolder) -> Money:
        return params.expected_next_year_net_income_per_share / params.growth_stage_profit_margin

    @staticmethod
    def value_of_equity(params: CompanyInputsHolder, info: TwoStageGrowthParams) -> Money:
        high_growth_times_bv_equity = params.first_stage_growth * EquityMultiplesEngine.book_value_of_equity(params)
        compound_first_stage_growth = (1 + params.first_stage_growth) ** params.years
        compound_second_stage_growth = (1 + params.second_stage_growth) ** params.years
        growth_stage_discount_minus_growth = info.cost_of_equity - params.first_stage_growth
        stable_stage_discount_minus_growth = info.cost_of_equity - params.second_stage_growth
        mod_compound_first_stage_growth = (1 + params.first_stage_growth) ** (params.years - 1)
        stable_growth_time_payout = (1 + params.second_stage_growth) * params.stable_stage_fcfe_percent_rev

        return (
            high_growth_times_bv_equity
            * params.growth_stage_fcfe_percent_rev
            * (1 - (compound_first_stage_growth / compound_second_stage_growth))
            / growth_stage_discount_minus_growth
        ) + (
            high_growth_times_bv_equity
            * mod_compound_first_stage_growth
            * stable_growth_time_payout
        ) / (stable_stage_discount_minus_growth * compound_second_stage_growth)

    @staticmethod
    def forward_pe(params: CompanyInputsHolder, info: TwoStageGrowthParams) -> Multiple:
        _value_of_equity = EquityMultiplesEngine.value_of_equity(params, info)
        return params.expected_next_year_net_income_per_share / _value_of_equity

    @staticmethod
    def price_to_book(params: CompanyInputsHolder, info: TwoStageGrowthParams) -> Multiple:
        _value_of_equity = EquityMultiplesEngine.value_of_equity(params, info)
        _book_value = EquityMultiplesEngine.book_value_of_equity(params)
        return _value_of_equity / _book_value

    @staticmethod
    def forward_price_to_sales(params: CompanyInputsHolder, info: TwoStageGrowthParams) -> Multiple:
        forward_pe_ratio = EquityMultiplesEngine.forward_pe(params, info)
        expected_rev_next_year = EquityMultiplesEngine.expected_revenues_next_year(params)
        return forward_pe_ratio * (params.expected_next_year_net_income_per_share / expected_rev_next_year)


@dataclass(frozen=True, slots=True)
class FirmMultiplesEngine:
    """
    Utility class for computing firm multiples using CompanyInputsHolder.
    """

    @staticmethod
    def growth_roic(params: CompanyInputsHolder) -> Percent:
        return params.first_stage_growth / params.growth_stage_reinvestment_rate

    @staticmethod
    def stable_roic(params: CompanyInputsHolder) -> Percent:
        return params.second_stage_growth / params.stable_stage_reinvestment_rate

    @staticmethod
    def enterprise_value(params: CompanyInputsHolder) -> Money:  # per share
        _ebit_after_reinvestment = params.expected_next_year_after_tax_ebit_per_share * (
            1 - params.growth_stage_reinvestment_rate
        )
        _compound_first_stage_growth = (1 + params.first_stage_growth) ** params.years
        _compound_growth_stage_wacc = (1 + params.growth_stage_wacc) ** params.years
        _growth_stage_wacc_minus_growth = params.growth_stage_wacc - params.first_stage_growth
        _stable_stage_wacc_minus_growth = params.stable_stage_wacc - params.second_stage_growth
        _mod_compound_first_stage_growth = (1 + params.first_stage_growth) ** (params.years - 1)
        _stable_growth_minus_reinvestment = (1 + params.second_stage_growth) * (
            1 - params.stable_stage_reinvestment_rate
        )

        return (
            _ebit_after_reinvestment
            * (1 - (_compound_first_stage_growth / _compound_growth_stage_wacc))
            / _growth_stage_wacc_minus_growth
        ) + (
            params.expected_next_year_after_tax_ebit_per_share
            * _mod_compound_first_stage_growth
            * _stable_growth_minus_reinvestment
        ) / (_stable_stage_wacc_minus_growth * _compound_growth_stage_wacc)

    # ---------------- EV/EBIT ----------------

    @staticmethod
    def forward_ev_over_ebit(snapshot: FinancialSnapshot, params: CompanyInputsHolder) -> Multiple:
        _enterprise_value = FirmMultiplesEngine.enterprise_value(params)
        _ebit_before_tax = params.expected_next_year_after_tax_ebit_per_share / (1 - snapshot.marginal_tax_rate)
        return _enterprise_value / _ebit_before_tax

    @staticmethod
    def trailing_ev_over_ebit(snapshot: FinancialSnapshot, params: CompanyInputsHolder) -> Multiple:
        _forward = FirmMultiplesEngine.forward_ev_over_ebit(snapshot, params)
        return _forward * (1 + params.first_stage_growth)

    # ---------------- EV/Sales ----------------

    @staticmethod
    def forward_ev_over_sales(params: CompanyInputsHolder) -> Multiple:
        #used params.expected_next...after_tax_ebit instead of just expected_next...
        _enterprise_value = FirmMultiplesEngine.enterprise_value(params)
        _expected_revenues_next_year = params.expected_next_year_after_tax_ebit_per_share/params.growth_stage_after_tax_ebit
        return _enterprise_value / _expected_revenues_next_year

    @staticmethod
    def trailing_ev_over_sales(params: CompanyInputsHolder) -> Multiple:
        _forward = FirmMultiplesEngine.forward_ev_over_sales(params)
        return _forward / (1 + params.first_stage_growth)

    

