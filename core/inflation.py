"""
core/inflation.py
Kenya Inflation Context Engine

Calculates the difference between nominal and real spending changes,
applying the Fisher equation to personal transaction data.

Core concept:
    Nominal change = the raw percentage change in spending (what you see)
    Real change    = the change adjusted for inflation (what it means)

    Real change = ((1 + nominal_change) / (1 + monthly_inflation)) - 1

This is a direct application of the Fisher equation, which relates
nominal and real rates — a foundational concept in macroeconomics
named after Irving Fisher (1867–1947).

Why this matters in Kenya:
    During 2022–2023, Kenya experienced food inflation above 10%.
    A household increasing food spending by 10% during this period
    was not consuming more — it was paying more for the same amount.
    This module makes that distinction visible in your personal data.
"""

from database.db import get_monthly_summaries_range
from data.kenya_cpi import (
    get_inflation_rate,
    get_current_inflation,
    annual_to_monthly,
    SSA_AVERAGE_INFLATION_2024,
    SSA_AVERAGE_INFLATION_2025,
)

# Maps our transaction categories to the appropriate CPI sub-index
CATEGORY_CPI_MAP = {
    "food":        "food",
    "transport":   "transport",
    "rent":        "headline",
    "utilities":   "headline",
    "health":      "headline",
    "entertainment": "headline",
}


def calculate_real_change(nominal_change: float, annual_inflation: float) -> float:
    """
    Apply the Fisher equation to find the real change from a nominal change.

    Arguments:
        nominal_change:   Fractional spending change (e.g. 0.10 = 10% increase)
        annual_inflation: Annual inflation rate as decimal (e.g. 0.046 = 4.6%)

    Returns:
        Real change as a fraction (e.g. 0.038 = 3.8% real increase)

    Formula:
        real = ((1 + nominal) / (1 + monthly_inflation)) - 1

    We convert the annual rate to monthly because our spending data
    is monthly — we are comparing one month to the next, not one year
    to the next.
    """
    monthly_inflation = annual_to_monthly(annual_inflation)
    return ((1 + nominal_change) / (1 + monthly_inflation)) - 1


def get_inflation_analysis(user_id: int) -> dict:
    """
    Generate the complete Kenya Inflation Context analysis.

    Compares the most recent month's spending to the previous month,
    then adjusts for Kenya's CPI to show real vs. nominal changes.

    Returns:
        {
            has_data:             bool
            months_of_data:       int
            current_month_label:  str  e.g. "2025-06"
            previous_month_label: str  e.g. "2025-05"
            headline_inflation:   float current annual headline rate
            ssa_inflation:        float Sub-Saharan Africa average
            total_nominal_change: float overall nominal spending change
            total_real_change:    float overall real spending change
            monthly_totals:       list  6-month series for the chart
            category_analysis:    dict  per-category results
        }
    """
    summaries = get_monthly_summaries_range(user_id, months=6)
    active    = [s for s in summaries if s["total_expenses"] > 0]

    if len(active) < 2:
        return {
            "has_data":      False,
            "months_of_data": len(active),
        }

    # Use the two most recent months that have data
    current  = active[-1]
    previous = active[-2]

    current_year  = current["year"]
    current_month = current["month"]

    headline_inflation = get_inflation_rate(current_year, current_month, "headline")

    # Regional comparison value
    ssa_inflation = (
        SSA_AVERAGE_INFLATION_2025
        if current_year >= 2025
        else SSA_AVERAGE_INFLATION_2024
    )

    # ── CATEGORY ANALYSIS ─────────────────────────────────────────────────────
    category_analysis = {}

    for category, cpi_type in CATEGORY_CPI_MAP.items():
        current_spend  = current["by_category"].get(category, 0)
        previous_spend = previous["by_category"].get(category, 0)

        if current_spend == 0 and previous_spend == 0:
            continue

        inflation_rate = get_inflation_rate(current_year, current_month, cpi_type)

        # Calculate nominal change
        if previous_spend > 0:
            nominal_change = (current_spend - previous_spend) / previous_spend
        elif current_spend > 0:
            nominal_change = 1.0   # New category — treat as 100% increase
        else:
            nominal_change = 0.0

        real_change     = calculate_real_change(nominal_change, inflation_rate)
        interpretation  = _interpret_change(nominal_change, real_change, category)

        category_analysis[category] = {
            "current_spend":   current_spend,
            "previous_spend":  previous_spend,
            "nominal_change":  nominal_change,
            "real_change":     real_change,
            "inflation_rate":  inflation_rate,
            "interpretation":  interpretation,
        }

    # ── OVERALL TOTALS ─────────────────────────────────────────────────────────
    if previous["total_expenses"] > 0:
        total_nominal_change = (
            (current["total_expenses"] - previous["total_expenses"])
            / previous["total_expenses"]
        )
    else:
        total_nominal_change = 0.0

    total_real_change = calculate_real_change(total_nominal_change, headline_inflation)

    # ── MONTHLY CHART SERIES ───────────────────────────────────────────────────
    # Build two series for the chart: nominal spending and inflation-adjusted spending.
    # We deflate each month relative to the first month in the series —
    # this shows the real spending trend over time.
    monthly_totals    = []
    cumulative_factor = 1.0

    for s in summaries:
        if s["total_expenses"] == 0:
            continue

        rate        = get_inflation_rate(s["year"], s["month"], "headline")
        monthly_r   = annual_to_monthly(rate)
        cumulative_factor *= (1 + monthly_r)

        monthly_totals.append({
            "label":         s["month_label"],
            "nominal_spend": s["total_expenses"],
            "real_spend":    s["total_expenses"] / cumulative_factor,
        })

    return {
        "has_data":             True,
        "months_of_data":       len(active),
        "current_month_label":  current["month_label"],
        "previous_month_label": previous["month_label"],
        "headline_inflation":   headline_inflation,
        "ssa_inflation":        ssa_inflation,
        "total_nominal_change": total_nominal_change,
        "total_real_change":    total_real_change,
        "monthly_totals":       monthly_totals,
        "category_analysis":    category_analysis,
    }


def _interpret_change(nominal: float, real: float, category: str) -> str:
    """
    Generate a plain-English sentence interpreting the nominal vs real change.
    This is what turns numbers into economic insight.
    """
    label = category.replace("_", " ")
    n_pct = nominal * 100
    r_pct = real    * 100

    if abs(nominal) < 0.01:
        return f"Your {label} spending was roughly unchanged from last month."

    if nominal > 0 and real > 0:
        if real < nominal * 0.4:
            return (
                f"Your {label} spending rose {n_pct:.1f}% nominally, but only "
                f"{r_pct:.1f}% in real terms — most of the increase reflects "
                f"price rises, not more consumption."
            )
        else:
            return (
                f"Your {label} spending rose {n_pct:.1f}% nominally "
                f"and {r_pct:.1f}% in real terms — a genuine increase in consumption."
            )
    elif nominal > 0 and real <= 0:
        return (
            f"Your {label} spending rose {n_pct:.1f}% nominally, but fell "
            f"{abs(r_pct):.1f}% in real terms — inflation accounts for the "
            f"entire increase."
        )
    else:
        return (
            f"Your {label} spending fell {abs(n_pct):.1f}% nominally "
            f"({abs(r_pct):.1f}% in real terms) — a genuine reduction."
        )
