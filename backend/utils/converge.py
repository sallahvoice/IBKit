"""file used in smoothing growth & decline in financials over time"""

from typing import List

from backend.utils.decorators import timing

Percent = float
Money = int


@timing
def converge_growth(
    start_growth: Percent, stable_growth: Percent, years: int
) -> List[Percent]:
    """
    Gradually converges from start_growth to stable_growth over a number of years.

    Args:
        start_growth (Percent): Initial growth rate.
        stable_growth (Percent): Final growth rate.
        years (int): Number of years to converge.

    Returns:
        List[Percent]: List of growth rates for each year.
    """
    if years <= 0:
        return []
    step = (stable_growth - start_growth) / years
    growths = []
    current = start_growth
    for _ in range(years):
        current += step
        growths.append(current)
    return growths


@timing
def project_revenue(
    last_annual_revenue: Money, growth_rates: List[Percent]
) -> List[Money]:
    """
    Projects future revenues based on initial revenue and a list of growth rates.

    Args:
        last_annual_revenue (Money): The most recent annual revenue.
        growth_rates (List[Percent]): Growth rates for each year.

    Returns:
        List[Money]: Projected revenues for each year (including initial).
    """
    revenues = [last_annual_revenue]
    for g in growth_rates:
        new_revenue = revenues[-1] * (1 + g)
        revenues.append(new_revenue)
    return revenues


@timing
def project_other_line_items(
    revenues: List[Money], percentages: List[Percent]
) -> List[Money]:
    """
    Projects other line items as a percentage of revenues.

    Args:
        revenues (List[Money]): List of revenues.
        percentages (List[Percent]): Corresponding percentages for each revenue.

    Returns:
        List[Money]: Projected line item values.
    """
    projected = []
    for rev, pct in zip(revenues, percentages):
        projected_value = pct * rev
        projected.append(projected_value)
    return projected
