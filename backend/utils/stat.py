from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class IndustryGroup(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    CONSUMER = "consumer"
    INDUSTRIAL = "industrial"
    ENERGY = "energy"
    UTILITIES = "utilities"
    REAL_ESTATE = "real_estate"


@dataclass(frozen=True, slots=True)
class FinancialSnapshot:
    """
    Core financial snapshot - Damodaran focuses on fundamental value drivers
    Removed optionals, focus on what actually drives value
    """

    # Identifiers
    company_id: str
    fiscal_year_end: datetime

    # Income Statement - Value Drivers (all in millions USD)
    revenue: Decimal
    ebitda: Decimal  # Operating performance before capital structure
    ebit: Decimal  # Operating income
    net_income: Decimal

    # Balance Sheet - Capital Structure
    total_assets: Decimal
    total_debt: Decimal  # Interest-bearing debt only
    cash: Decimal  # Cash and marketable securities
    book_equity: Decimal  # Shareholders' equity

    # Cash Generation
    operating_cash_flow: Decimal
    capex: Decimal  # Capital expenditures

    # Market Data
    shares_outstanding: Decimal
    market_cap: Decimal  # Current market value

    def __post_init__(self):
        """Damodaran-style validation - focus on economic reality"""
        if self.revenue <= 0:
            raise ValueError(f"Revenue must be positive: {self.revenue}")

        if self.shares_outstanding <= 0:
            raise ValueError(
                f"Shares outstanding must be positive: {self.shares_outstanding}"
            )

        if self.market_cap <= 0:
            raise ValueError(f"Market cap must be positive: {self.market_cap}")

    @property
    def enterprise_value(self) -> Decimal:
        """EV = Market Cap + Net Debt (fundamental to Damodaran's approach)"""
        net_debt = self.total_debt - self.cash
        return self.market_cap + net_debt

    @property
    def free_cash_flow(self) -> Decimal:
        """FCF = Operating Cash Flow - Capex"""
        return self.operating_cash_flow - self.capex

    @property
    def invested_capital(self) -> Decimal:
        """Book value of invested capital"""
        return self.book_equity + self.total_debt

    @property
    def ebitda_margin(self) -> Decimal:
        """EBITDA as % of revenue - profitability measure"""
        return (self.ebitda / self.revenue) if self.revenue > 0 else Decimal("0")

    @property
    def return_on_invested_capital(self) -> Decimal:
        """ROIC = EBIT(1-Tax Rate) / Invested Capital - key value driver"""
        # Simplified: assume 25% tax rate for ROIC calculation
        after_tax_ebit = self.ebit * Decimal("0.75")
        return (
            (after_tax_ebit / self.invested_capital)
            if self.invested_capital > 0
            else Decimal("0")
        )


@dataclass(frozen=True, slots=True)
class ComparableCompany:
    """
    Single comparable company for multiples analysis
    Focus on fundamental multiples that relate to value drivers
    """

    company_id: str
    company_name: str
    industry_group: IndustryGroup

    # Current multiples (computed from FinancialSnapshot)
    ev_revenue: Decimal  # EV / Revenue
    ev_ebitda: Decimal  # EV / EBITDA
    pe_ratio: Decimal  # Price / Earnings

    # Fundamental drivers (why the multiples are what they are)
    revenue_growth: Decimal  # Last year growth rate
    ebitda_margin: Decimal  # Profitability
    roic: Decimal  # Return on invested capital

    @classmethod
    def from_financial_snapshot(
        cls,
        snapshot: "FinancialSnapshot",
        company_name: str,
        industry_group: IndustryGroup,
        prior_year_revenue: Decimal,
    ) -> "ComparableCompany":
        """Create comparable from financial snapshot"""

        # Calculate multiples
        ev_revenue = (
            snapshot.enterprise_value / snapshot.revenue
            if snapshot.revenue > 0
            else Decimal("0")
        )
        ev_ebitda = (
            snapshot.enterprise_value / snapshot.ebitda
            if snapshot.ebitda > 0
            else Decimal("0")
        )
        pe_ratio = (
            snapshot.market_cap / snapshot.net_income
            if snapshot.net_income > 0
            else Decimal("0")
        )

        # Calculate growth rate
        revenue_growth = (
            (snapshot.revenue - prior_year_revenue) / prior_year_revenue
            if prior_year_revenue > 0
            else Decimal("0")
        )

        return cls(
            company_id=snapshot.company_id,
            company_name=company_name,
            industry_group=industry_group,
            ev_revenue=ev_revenue,
            ev_ebitda=ev_ebitda,
            pe_ratio=pe_ratio,
            revenue_growth=revenue_growth,
            ebitda_margin=snapshot.ebitda_margin,
            roic=snapshot.return_on_invested_capital,
        )

    @property
    def drivers_tuple(self) -> tuple[float, float, float]:
        """(growth, ebitda_margin, roic) as floats for regression."""
        return (
            float(self.revenue_growth),
            float(self.ebitda_margin),
            float(self.roic),
        )

    @property
    def multiples_tuple(self) -> tuple[float, float, float]:
        """(ev/rev, ev/ebitda, pe) as floats for robust stats/regression."""
        return (
            float(self.ev_revenue),
            float(self.ev_ebitda),
            float(self.pe_ratio),
        )


from decimal import Decimal
from typing import Callable, Dict, List, Optional, Tuple


# -------- Robust stats helpers --------
def _median(xs: List[float]) -> float:
    ys = sorted(xs)
    n = len(ys)
    if n == 0:
        return float("nan")
    mid = n // 2
    return ys[mid] if n % 2 == 1 else 0.5 * (ys[mid - 1] + ys[mid])


def _iqr_filter(xs: List[float], k: float = 1.5) -> List[float]:
    if len(xs) < 4:
        return xs
    ys = sorted(xs)
    n = len(ys)
    q1 = ys[n // 4]
    q3 = ys[(3 * n) // 4]
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return [x for x in xs if lo <= x <= hi]


def _winsorize(xs: List[float], p: float = 0.05) -> List[float]:
    """Clamp to p/1-p quantiles; requires len>=2."""
    if not xs:
        return xs
    ys = sorted(xs)
    n = len(ys)
    if n < 3:
        return ys
    lo_idx = max(0, int(p * (n - 1)))
    hi_idx = min(n - 1, int((1 - p) * (n - 1)))
    lo, hi = ys[lo_idx], ys[hi_idx]
    return [min(max(x, lo), hi) for x in ys]


# -------- Minimal OLS on up to 3 predictors (X includes intercept) --------
def _ols_fit(X: List[List[float]], y: List[float]) -> Optional[List[float]]:
    """
    Returns beta vector using normal equations (X'X)^-1 X'y.
    Small, stable sets only; returns None on singular matrix.
    """
    try:
        # Build XtX and Xty
        p = len(X[0])
        XtX = [[0.0] * p for _ in range(p)]
        Xty = [0.0] * p
        for i in range(len(X)):
            xi = X[i]
            yi = y[i]
            for a in range(p):
                Xty[a] += xi[a] * yi
                for b in range(p):
                    XtX[a][b] += xi[a] * xi[b]

        # Solve XtX * beta = Xty via Gaussian elimination
        # Augment matrix
        A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
        # Elimination
        n = len(A)
        for i in range(n):
            # pivot
            pivot = i
            for r in range(i + 1, n):
                if abs(A[r][i]) > abs(A[pivot][i]):
                    pivot = r
            if abs(A[pivot][i]) < 1e-12:
                return None
            A[i], A[pivot] = A[pivot], A[i]
            # normalize
            div = A[i][i]
            for c in range(i, n + 1):
                A[i][c] /= div
            # eliminate others
            for r in range(n):
                if r == i:
                    continue
                factor = A[r][i]
                for c in range(i, n + 1):
                    A[r][c] -= factor * A[i][c]
        beta = [A[i][n] for i in range(n)]
        return beta
    except Exception:
        return None


from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ComparableAnalysis:
    """
    link multiples to fundamentals; robust stats + optional regression.
    """

    target_company_id: str
    analysis_date: datetime
    industry_group: IndustryGroup
    comparables: List[ComparableCompany] = field(default_factory=list)

    # Tuning knobs
    min_sample: int = 5
    winsor_p: float = 0.05
    use_regression_if_n: int = 8  # need enough breadth to regress

    def __post_init__(self):
        if len(self.comparables) < 3:
            raise ValueError("Need at least 3 comparable companies")

    # ---- Cleaned universes per multiple ----
    def _valid_ev_rev(self) -> List[ComparableCompany]:
        return [
            c
            for c in self.comparables
            if c.ev_revenue > 0 and c.revenue_growth is not None
        ]

    def _valid_ev_ebitda(self) -> List[ComparableCompany]:
        return [c for c in self.comparables if c.ev_ebitda > 0 and c.ebitda_margin > 0]

    def _valid_pe(self) -> List[ComparableCompany]:
        return [c for c in self.comparables if c.pe_ratio > 0 and c.roic > 0]

    # ---- Robust aggregations ----
    def _robust_center(self, xs: List[float]) -> Optional[float]:
        if len(xs) < self.min_sample and xs:
            # Small sample: just median of winsorized
            return _median(_winsorize(xs, self.winsor_p))
        if not xs:
            return None
        # Winsorize then median (stable against tails)
        return _median(_winsorize(xs, self.winsor_p))

    @property
    def robust_medians(self) -> Dict[str, Optional[Decimal]]:
        ev_rev = [float(c.ev_revenue) for c in self._valid_ev_rev()]
        ev_ebitda = [float(c.ev_ebitda) for c in self._valid_ev_ebitda()]
        pe = [float(c.pe_ratio) for c in self._valid_pe()]

        return {
            "ev_rev": Decimal(str(self._robust_center(ev_rev))) if ev_rev else None,
            "ev_ebitda": (
                Decimal(str(self._robust_center(ev_ebitda))) if ev_ebitda else None
            ),
            "pe": Decimal(str(self._robust_center(pe))) if pe else None,
        }

    # ---- Regression-adjusted multiples (optional) ----
    def _regress_multiple_on_drivers(
        self,
        comps: List[ComparableCompany],
        selector: Callable[[ComparableCompany], float],
    ) -> Optional[Tuple[List[float], List[str]]]:
        """
        Returns (beta, features) for multiple ~ a + b1*growth + b2*margin + b3*roic
        where features order: ['intercept','growth','margin','roic']
        """
        if len(comps) < self.use_regression_if_n:
            return None
        # Build X (with intercept) and y
        X, y = [], []
        for c in comps:
            m = selector(c)
            if m <= 0:
                continue
            g, mrg, rc = c.drivers_tuple
            if any(map(lambda v: v != v or v is None, (g, mrg, rc))):  # NaN check
                continue
            X.append([1.0, g, mrg, rc])
            y.append(float(m))
        if len(X) < self.use_regression_if_n:
            return None
        beta = _ols_fit(X, y)
        if beta is None:
            return None
        return beta, ["intercept", "growth", "margin", "roic"]

    def regression_adjusted_multiples_for_target(
        self, target_growth: Decimal, target_margin: Decimal, target_roic: Decimal
    ) -> Dict[str, Optional[Decimal]]:
        # Prepare target driver vector
        tg, tm, tr = float(target_growth), float(target_margin), float(target_roic)
        X_target = [1.0, tg, tm, tr]

        out: Dict[str, Optional[Decimal]] = {
            "ev_rev": None,
            "ev_ebitda": None,
            "pe": None,
        }

        # EV/Revenue regression
        rr = self._regress_multiple_on_drivers(
            self._valid_ev_rev(), lambda c: float(c.ev_revenue)
        )
        if rr is not None:
            beta, _ = rr
            pred = sum(beta[i] * X_target[i] for i in range(len(beta)))
            if pred > 0:
                out["ev_rev"] = Decimal(str(pred))

        # EV/EBITDA regression
        re = self._regress_multiple_on_drivers(
            self._valid_ev_ebitda(), lambda c: float(c.ev_ebitda)
        )
        if re is not None:
            beta, _ = re
            pred = sum(beta[i] * X_target[i] for i in range(len(beta)))
            if pred > 0:
                out["ev_ebitda"] = Decimal(str(pred))

        # P/E regression
        rp = self._regress_multiple_on_drivers(
            self._valid_pe(), lambda c: float(c.pe_ratio)
        )
        if rp is not None:
            beta, _ = rp
            pred = sum(beta[i] * X_target[i] for i in range(len(beta)))
            if pred > 0:
                out["pe"] = Decimal(str(pred))

        return out


def value_using_comps(
    snapshot: FinancialSnapshot,
    analysis: ComparableAnalysis,
    use_regression: bool = True,
) -> List[ValuationResult]:
    """
    Produces ValuationResults using:
      - regression-adjusted multiples if available (growth, margin, ROIC),
      - otherwise robust medians.
    Skips methods with invalid denominators (e.g., negative EBITDA/Earnings).
    """
    results: List[ValuationResult] = []
    today = analysis.analysis_date

    # Target drivers
    t_growth = Decimal("0")  # if you have trailing growth, plug it here; otherwise 0
    t_margin = snapshot.ebitda_margin
    t_roic = snapshot.return_on_invested_capital

    # Choose multiples
    multiples = analysis.robust_medians
    if use_regression:
        reg = analysis.regression_adjusted_multiples_for_target(
            t_growth, t_margin, t_roic
        )
        # Prefer regression value when present & positive
        for k in ("ev_rev", "ev_ebitda", "pe"):
            if reg.get(k) and reg[k] > 0:
                multiples[k] = reg[k]

    # Helper to bridge to equity/share
    def finalize(ev: Decimal, method_label: str) -> Optional[ValuationResult]:
        if ev is None or ev <= 0:
            return None
        net_debt = snapshot.total_debt - snapshot.cash
        equity = ev - net_debt
        if equity <= 0 or snapshot.shares_outstanding <= 0:
            return None
        per_share = equity / snapshot.shares_outstanding
        if per_share <= 0:
            return None
        return ValuationResult(
            company_id=snapshot.company_id,
            valuation_date=today,
            method=method_label,
            enterprise_value=ev,
            equity_value=equity,
            value_per_share=per_share,
            assumptions_used={
                "multiple": method_label,
                "drivers_used": {
                    "revenue_growth": str(t_growth),
                    "ebitda_margin": str(t_margin),
                    "roic": str(t_roic),
                },
            },
        )

    # EV/Revenue
    if multiples.get("ev_rev") and snapshot.revenue > 0:
        ev = multiples["ev_rev"] * snapshot.revenue
        r = finalize(ev, "EV/Revenue (Damodaran robust)")
        if r:
            results.append(r)

    # EV/EBITDA
    if multiples.get("ev_ebitda") and snapshot.ebitda > 0:
        ev = multiples["ev_ebitda"] * snapshot.ebitda
        r = finalize(ev, "EV/EBITDA (Damodaran robust)")
        if r:
            results.append(r)

    # P/E (equity-side multiple; compute equity value first, then back-solve an 'EV' for storage)
    if (
        multiples.get("pe")
        and snapshot.net_income > 0
        and snapshot.shares_outstanding > 0
    ):
        price_per_share = multiples["pe"] * (
            snapshot.net_income / snapshot.shares_outstanding
        )
        equity_value = price_per_share * snapshot.shares_outstanding
        # fabricate EV for consistency in ValuationResult
        ev = equity_value + (snapshot.total_debt - snapshot.cash)
        r = finalize(ev, "P/E (Damodaran robust)")
        if r:
            results.append(r)

    return results


def value_target_with_both_methods(
    profile: CompanyValuationProfile,
) -> Dict[str, object]:
    """
    Returns both: Two-Stage DCF + Comps array.
    """
    projections, dcf = run_two_stage_dcf(
        profile.financial_snapshot,
        profile.growth_params,
        valuation_date=profile.comparable_analysis.analysis_date,
    )
    comps_results = value_using_comps(
        snapshot=profile.financial_snapshot,
        analysis=profile.comparable_analysis,
        use_regression=True,
    )
    return {
        "projections": projections,
        "dcf_result": dcf,
        "comps_results": comps_results,
    }
