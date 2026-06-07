"""
core/projection.py
Wealth Projection Engine

Projects future net worth under four scenarios using compound growth.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT — ASSUMPTIONS AND LIMITATIONS

All return rates in this module are ASSUMPTIONS based on historical
market data. Past performance does not predict future returns.
These projections are educational tools for understanding the mechanics
of compound growth, not financial advice or investment guidance.

Default return assumption:
    7% nominal annual return — a conservative estimate based on the
    Nairobi Securities Exchange (NSE) All-Share Index long-run average.
    This is deliberately below the US S&P 500 long-run average (~10%)
    to account for emerging market risk, transaction costs, and the
    lower liquidity of the NSE compared to developed markets.

Users can adjust the return rate assumption using the slider on the
Wealth Projection page to explore how different market environments
would affect their long-term outcomes.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Economic concepts demonstrated:
    1. Compound interest      — Small rate differences grow into enormous
                               gaps over long time horizons.
    2. Intertemporal choice   — Financial decisions today have
                               consequences decades in the future.
    3. Real vs nominal wealth — Inflation silently erodes nominal growth.
    4. Return premium         — The wealth gap between consistently
                               investing vs. holding savings in cash.

The formula used is the Future Value of an annuity:
    FV = P(1+r)^n  +  C × [((1+r)^n − 1) / r]

Where:
    P = current balance (starting principal)
    r = monthly return rate (annual rate converted to monthly)
    n = number of months
    C = monthly savings contribution
"""

from database.db import get_current_balance, get_monthly_summaries_range
from data.kenya_cpi import get_current_inflation

# ── CONSTANTS (clearly labelled as assumptions) ───────────────────────────────

NOMINAL_RETURN_RATE    = 0.07   # 7% annual — conservative NSE estimate (ASSUMPTION)
ACTIVE_RETURN_PREMIUM  = 0.03   # +3% premium: consistent equity vs. mixed/cash savings
IMPROVED_SAVINGS_BOOST = 0.05   # +5 percentage points for the savings discipline scenario
PROJECTION_YEARS       = 25     # Maximum years to project

# Bounds for the user-adjustable return rate slider
MIN_RETURN_RATE = 0.03          # 3% floor — approximately inflation-neutral
MAX_RETURN_RATE = 0.14          # 14% ceiling — optimistic but plausible NSE equity


def compound_growth(
    principal: float,
    monthly_contribution: float,
    annual_rate: float,
    years: int,
) -> list[float]:
    """
    Calculate projected net worth at each year from year 1 to 'years'.

    Arguments:
        principal:            Current balance today
        monthly_contribution: Amount saved/invested per month
        annual_rate:          Expected annual return as a decimal (e.g. 0.07)
                              NOTE: This is an assumption, not a prediction.
        years:                Number of years to project

    Returns:
        A list of projected net worth values, one per year.
        Index 0 = end of year 1, index 24 = end of year 25.

    Note on monthly rate conversion:
        Uses (1 + annual)^(1/12) - 1 rather than annual/12.
        The compound conversion is mathematically correct for
        continuously compounding returns.
    """
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    projections = []

    for year in range(1, years + 1):
        n = year * 12

        fv_principal = principal * (1 + monthly_rate) ** n

        if monthly_rate > 0:
            fv_contributions = monthly_contribution * (
                ((1 + monthly_rate) ** n - 1) / monthly_rate
            )
        else:
            fv_contributions = monthly_contribution * n

        projections.append(fv_principal + fv_contributions)

    return projections


def get_projection_data(
    user_id: int,
    custom_savings_rate: float = None,
    custom_return_rate: float = None,
) -> dict:
    """
    Build all four projection scenarios for a user.

    Arguments:
        user_id:             The logged-in user's ID
        custom_savings_rate: If provided (from the savings rate slider),
                             overrides the user's actual recorded savings rate.
        custom_return_rate:  If provided (from the return rate slider),
                             overrides the default 7% assumption.
                             Expressed as a percentage (e.g. 8.5 for 8.5%).

    Four scenarios returned:
        1. current_path   — Actual savings rate, user-selected return assumption
        2. improved_path  — Savings rate +5%, same return (discipline improvement)
        3. active_path    — Same savings, +3% return (consistent equity vs cash)
        4. real_path      — Current path, inflation-adjusted (real purchasing power)

    Returns:
        {
            has_data:              bool
            years:                 list[int] [1..25]
            current_path:          list[float]
            improved_path:         list[float]
            active_path:           list[float]
            real_path:             list[float]
            current_balance:       float
            monthly_income:        float
            monthly_savings:       float
            avg_monthly_expenses:  float
            actual_savings_rate:   float (%)
            resilience_months:     float — months of expenses covered by balance
            return_rate:           float — actual return rate used (decimal)
            active_return_rate:    float — return rate for active scenario (decimal)
            at_10_years:           dict {current, improved, active, real}
            at_25_years:           dict {current, improved, active, real}
            inflation_rate:        float
            real_return_rate:      float
        }
    """
    summaries     = get_monthly_summaries_range(user_id, months=6)
    income_months = [s for s in summaries if s["total_income"] > 0]

    if not income_months:
        return {"has_data": False}

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
        effective_savings = max(avg_savings, 0.0)

    # Determine effective return rate (user assumption or default)
    if custom_return_rate is not None:
        effective_return = max(
            MIN_RETURN_RATE,
            min(MAX_RETURN_RATE, custom_return_rate / 100)
        )
    else:
        effective_return = NOMINAL_RETURN_RATE

    current_balance   = get_current_balance(user_id)
    current_inflation = get_current_inflation()

    # Real return = nominal return adjusted for inflation (Fisher equation)
    real_return_rate = (1 + effective_return) / (1 + current_inflation) - 1

    # Active investment return: same savings redirected to consistent equity
    # models the premium from disciplined NSE investing vs. mixed/cash savings
    active_return_rate = min(effective_return + ACTIVE_RETURN_PREMIUM, MAX_RETURN_RATE)

    # Financial resilience: months of expenses the current balance covers
    resilience_months = (
        current_balance / avg_expenses if avg_expenses > 0 else 0.0
    )

    # ── FOUR SCENARIOS ────────────────────────────────────────────────────────

    # 1: Current behaviour (effective savings rate, user-selected return)
    current_path = compound_growth(
        principal=current_balance,
        monthly_contribution=effective_savings,
        annual_rate=effective_return,
        years=PROJECTION_YEARS,
    )

    # 2: Savings discipline (+5 percentage points on savings rate)
    improved_monthly_savings = avg_income * ((effective_rate + IMPROVED_SAVINGS_BOOST) / 100)
    improved_path = compound_growth(
        principal=current_balance,
        monthly_contribution=improved_monthly_savings,
        annual_rate=effective_return,
        years=PROJECTION_YEARS,
    )

    # 3: Active investment (same savings rate, +3% return from consistent equity)
    active_path = compound_growth(
        principal=current_balance,
        monthly_contribution=effective_savings,
        annual_rate=active_return_rate,
        years=PROJECTION_YEARS,
    )

    # 4: Real wealth (current path, inflation-adjusted purchasing power)
    real_path = compound_growth(
        principal=current_balance,
        monthly_contribution=effective_savings,
        annual_rate=max(real_return_rate, 0.0),
        years=PROJECTION_YEARS,
    )

    return {
        "has_data":             True,
        "years":                list(range(1, PROJECTION_YEARS + 1)),
        "current_path":         current_path,
        "improved_path":        improved_path,
        "active_path":          active_path,
        "real_path":            real_path,
        "current_balance":      current_balance,
        "monthly_income":       avg_income,
        "monthly_savings":      effective_savings,
        "avg_monthly_expenses": round(avg_expenses, 2),
        "actual_savings_rate":  round(actual_savings_rate, 1),
        "resilience_months":    round(resilience_months, 1),
        "return_rate":          effective_return,
        "active_return_rate":   active_return_rate,
        "at_10_years": {
            "current":  current_path[9],
            "improved": improved_path[9],
            "active":   active_path[9],
            "real":     real_path[9],
        },
        "at_25_years": {
            "current":  current_path[24],
            "improved": improved_path[24],
            "active":   active_path[24],
            "real":     real_path[24],
        },
        "inflation_rate":   current_inflation,
        "real_return_rate": real_return_rate,
    }
