"""
core/projection.py
Wealth Projection Engine

Projects future net worth under three scenarios using compound growth.

Economic concepts demonstrated:
    1. Compound interest — Small rate differences compound into enormous
                           gaps over long time horizons.
    2. Intertemporal choice — How financial decisions made today affect
                              future wealth (a core topic in financial economics).
    3. Real vs nominal returns — A 7% return with 4% inflation is a
                                  ~2.9% real return. Inflation silently
                                  erodes nominal wealth.

The formula used is the Future Value of an annuity:
    FV = P(1+r)^n  +  C × [((1+r)^n − 1) / r]

Where:
    P = current balance (starting principal)
    r = monthly return rate (annual rate converted to monthly)
    n = number of months
    C = monthly savings contribution

Return rate assumption:
    7% nominal annual return. This is a conservative estimate based on
    the Nairobi Securities Exchange (NSE) All-Share Index historical
    average. It is below the long-run US S&P 500 average (~10%) to
    account for emerging market risk and transaction costs.
"""

from database.db import get_current_balance, get_monthly_summaries_range
from data.kenya_cpi import get_current_inflation

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
NOMINAL_RETURN_RATE      = 0.07   # 7% annual — conservative NSE estimate
IMPROVED_SAVINGS_BOOST   = 0.05   # +5 percentage points for the improved scenario
PROJECTION_YEARS         = 25     # Maximum years to project


def compound_growth(
    principal: float,
    monthly_contribution: float,
    annual_rate: float,
    years: int,
) -> list[float]:
    """
    Calculate projected net worth at each year from year 1 to 'years'.

    Arguments:
        principal:            Current balance today (KES)
        monthly_contribution: Amount saved/invested per month (KES)
        annual_rate:          Expected annual return as a decimal (e.g. 0.07)
        years:                Number of years to project

    Returns:
        A list of projected net worth values, one per year.
        Index 0 = end of year 1, index 24 = end of year 25.

    Note on monthly rate conversion:
        We use (1 + annual)^(1/12) - 1 rather than annual/12.
        The compound conversion is mathematically correct for
        continuously compounding returns.
    """
    # Convert annual rate to monthly using the compound formula
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    projections = []

    for year in range(1, years + 1):
        n = year * 12   # Total months elapsed

        # Future value of the lump-sum principal
        fv_principal = principal * (1 + monthly_rate) ** n

        # Future value of the monthly contributions (annuity formula)
        if monthly_rate > 0:
            fv_contributions = monthly_contribution * (
                ((1 + monthly_rate) ** n - 1) / monthly_rate
            )
        else:
            # Edge case: zero return rate — just accumulate contributions
            fv_contributions = monthly_contribution * n

        projections.append(fv_principal + fv_contributions)

    return projections


def get_projection_data(user_id: int, custom_savings_rate: float = None) -> dict:
    """
    Build all three projection scenarios for a user.

    Arguments:
        user_id:             The logged-in user's ID
        custom_savings_rate: If provided (from the page slider), uses this
                             rate instead of the user's actual recorded rate.
                             Allows "what if" exploration.

    Returns:
        {
            has_data:            bool
            years:               list[int] [1..25]
            current_path:        list[float] — actual/custom savings rate
            improved_path:       list[float] — savings rate + 5%
            real_path:           list[float] — inflation-adjusted returns
            current_balance:     float
            monthly_income:      float
            monthly_savings:     float
            actual_savings_rate: float (%)
            at_10_years:         dict  {current, improved, real}
            at_25_years:         dict  {current, improved, real}
            inflation_rate:      float current Kenya headline rate
            real_return_rate:    float nominal return minus inflation effect
        }
    """
    summaries     = get_monthly_summaries_range(user_id, months=6)
    income_months = [s for s in summaries if s["total_income"] > 0]

    if not income_months:
        return {"has_data": False}

    # Calculate average monthly figures from recorded data
    avg_income   = sum(s["total_income"]   for s in income_months) / len(income_months)
    avg_expenses = sum(s["total_expenses"] for s in income_months) / len(income_months)
    avg_savings  = avg_income - avg_expenses

    actual_savings_rate = (avg_savings / avg_income * 100) if avg_income > 0 else 0.0

    # Determine effective savings for projections
    if custom_savings_rate is not None:
        effective_rate    = custom_savings_rate
        effective_savings = avg_income * (custom_savings_rate / 100)
    else:
        effective_rate    = actual_savings_rate
        effective_savings = max(avg_savings, 0.0)   # Cannot save a negative amount

    current_balance   = get_current_balance(user_id)
    current_inflation = get_current_inflation()

    # Real return = nominal return adjusted for inflation
    # Formula: (1 + nominal) / (1 + inflation) - 1
    real_return_rate = (1 + NOMINAL_RETURN_RATE) / (1 + current_inflation) - 1

    # ── THREE SCENARIOS ───────────────────────────────────────────────────────

    # Scenario 1: Current path (effective savings rate, nominal 7% return)
    current_path = compound_growth(
        principal=current_balance,
        monthly_contribution=effective_savings,
        annual_rate=NOMINAL_RETURN_RATE,
        years=PROJECTION_YEARS,
    )

    # Scenario 2: Improved savings (effective rate + 5%, nominal 7% return)
    improved_monthly_savings = avg_income * ((effective_rate + IMPROVED_SAVINGS_BOOST) / 100)
    improved_path = compound_growth(
        principal=current_balance,
        monthly_contribution=improved_monthly_savings,
        annual_rate=NOMINAL_RETURN_RATE,
        years=PROJECTION_YEARS,
    )

    # Scenario 3: Real path (effective savings rate, inflation-adjusted return)
    real_path = compound_growth(
        principal=current_balance,
        monthly_contribution=effective_savings,
        annual_rate=real_return_rate,
        years=PROJECTION_YEARS,
    )

    return {
        "has_data":            True,
        "years":               list(range(1, PROJECTION_YEARS + 1)),
        "current_path":        current_path,
        "improved_path":       improved_path,
        "real_path":           real_path,
        "current_balance":     current_balance,
        "monthly_income":      avg_income,
        "monthly_savings":     effective_savings,
        "actual_savings_rate": round(actual_savings_rate, 1),
        "at_10_years": {
            "current":  current_path[9],
            "improved": improved_path[9],
            "real":     real_path[9],
        },
        "at_25_years": {
            "current":  current_path[24],
            "improved": improved_path[24],
            "real":     real_path[24],
        },
        "inflation_rate":    current_inflation,
        "real_return_rate":  real_return_rate,
    }
