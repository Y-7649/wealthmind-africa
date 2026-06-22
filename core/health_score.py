"""
core/health_score.py
Financial Health Score Engine

Calculates a composite Financial Health Score (0–100) across four dimensions.
Each dimension corresponds to a named concept in personal finance and
macroeconomic theory.

The composite methodology mirrors how financial institutions build
composite indices — the same approach used by:
    - Credit bureaus (weighted sub-scores → single credit score)
    - World Bank Human Development Index (HDI)
    - IMF Financial Soundness Indicators

Dimensions and their academic foundations:
    1. Savings Rate          — Friedman's Permanent Income Hypothesis (1957)
    2. Emergency Fund        — Buffer stock saving theory (Deaton, 1991)
    3. Spending Consistency  — Consumption smoothing (Hall, 1978)
    4. Investment Commitment — Capital accumulation (Solow growth model)

Weights:
    Savings Rate:   35% — most direct indicator of financial discipline
    Emergency Fund: 30% — determines resilience to income shocks
    Consistency:    20% — reveals spending behaviour patterns
    Commitment:     15% — lower weight as young adults may not yet invest formally
"""

import statistics
from database.db import get_current_balance, get_monthly_summaries_range


# ── COMPOSITE WEIGHTS (single source of truth) ────────────────────────────────
# Defined at module level so the Financial Health Score is computed identically
# wherever it is needed — the long-term tracker (calculate_health_score below)
# AND the Quick Assessment (core/assessment.py) import this exact dict. There is
# only one definition of how the four dimensions combine.
HEALTH_WEIGHTS = {
    "savings_rate":   0.35,   # most direct indicator of financial discipline
    "emergency_fund": 0.30,   # determines resilience to income shocks
    "consistency":    0.20,   # reveals spending behaviour patterns
    "commitment":     0.15,   # lower weight — young adults may not yet invest
}


# ── SCORING FUNCTIONS ─────────────────────────────────────────────────────────
# Each function converts a raw value to a 0–100 score using
# linear interpolation between research-based benchmark points.

def _score_savings_rate(rate_pct: float) -> float:
    """
    Convert savings rate (%) to a 0–100 score.

    Benchmarks:
        Below 10%:  Insufficient (red)   → 0–35 points
        10–20%:     Adequate (amber)      → 35–70 points
        20–30%:     Strong (green)        → 70–100 points
        Above 30%:  Excellent             → 100 points

    Economic basis: Friedman's permanent income hypothesis predicts
    that rational agents save a stable fraction of their permanent income.
    The 20% savings rate is the widely-cited benchmark from personal
    finance research and financial planning literature.
    """
    if rate_pct <= 0:
        return 0.0
    elif rate_pct <= 10:
        return (rate_pct / 10) * 35
    elif rate_pct <= 20:
        return 35 + ((rate_pct - 10) / 10) * 35
    elif rate_pct <= 30:
        return 70 + ((rate_pct - 20) / 10) * 30
    else:
        return 100.0


def _score_emergency_fund(months: float) -> float:
    """
    Convert emergency fund coverage (months of expenses) to a 0–100 score.

    Benchmarks:
        Below 1 month:  Critical vulnerability → 0–25 points
        1–3 months:     Basic buffer           → 25–60 points
        3–6 months:     Recommended range      → 60–90 points
        Above 6 months: Strong resilience       → 90–100 points

    Economic basis: Buffer stock saving theory (Deaton, 1991) shows
    that households need liquid reserves to maintain consumption during
    income shocks without resorting to costly credit. The 3–6 month
    standard is recommended by financial regulators and planners globally.
    """
    if months <= 0:
        return 0.0
    elif months <= 1:
        return (months / 1) * 25
    elif months <= 3:
        return 25 + ((months - 1) / 2) * 35
    elif months <= 6:
        return 60 + ((months - 3) / 3) * 30
    else:
        return min(100.0, 90 + ((months - 6) / 6) * 10)


def _score_spending_consistency(cv: float) -> float:
    """
    Convert the coefficient of variation (CV) of monthly expenses to a score.
    Lower CV = more consistent spending = higher score.

    CV = standard deviation ÷ mean

    Benchmarks:
        CV 0.0–0.1:  Very consistent  → 80–100 points
        CV 0.1–0.3:  Moderate         → 50–80 points
        CV 0.3–0.5:  Inconsistent     → 20–50 points
        CV above 0.5: Very erratic    → 0–20 points

    Economic basis: Consumption smoothing (Hall, 1978). Under the
    permanent income hypothesis, rational agents smooth consumption
    relative to their permanent income. High variability in spending
    may indicate income shocks, impulsive spending, or present bias.
    """
    if cv <= 0:
        return 100.0
    elif cv <= 0.1:
        return 100 - (cv / 0.1) * 20
    elif cv <= 0.3:
        return 80 - ((cv - 0.1) / 0.2) * 30
    elif cv <= 0.5:
        return 50 - ((cv - 0.3) / 0.2) * 30
    else:
        return max(0.0, 20 - ((cv - 0.5) / 0.5) * 20)


def _score_investment_commitment(rate_pct: float) -> float:
    """
    Convert investment commitment rate (%) to a 0–100 score.

    We use 'savings_transfer' category transactions as a proxy —
    money deliberately moved away from current consumption.

    Benchmarks:
        0%:     No investment        → 0 points
        1–5%:   Building the habit   → 0–50 points
        5–10%:  Meaningful commitment → 50–80 points
        10–15%: Strong commitment     → 80–100 points

    Economic basis: Capital accumulation. Even small, consistent
    investment rates compound substantially over long time horizons —
    demonstrated directly in the Wealth Projection module.
    """
    if rate_pct <= 0:
        return 0.0
    elif rate_pct <= 5:
        return (rate_pct / 5) * 50
    elif rate_pct <= 10:
        return 50 + ((rate_pct - 5) / 5) * 30
    elif rate_pct <= 15:
        return 80 + ((rate_pct - 10) / 5) * 20
    else:
        return 100.0


# ── PUBLIC SCORING API (shared with core/assessment.py) ───────────────────────
# The four scoring curves above are the canonical mapping from a raw economic
# quantity to a 0–100 sub-score. They are exposed here under public names so the
# Quick Assessment scores a respondent on the IDENTICAL curves the tracker uses.
# One implementation, one source of truth — the assessment cannot drift.
score_savings_rate          = _score_savings_rate
score_emergency_fund        = _score_emergency_fund
score_spending_consistency  = _score_spending_consistency
score_investment_commitment = _score_investment_commitment


# ── MAIN CALCULATION FUNCTION ─────────────────────────────────────────────────

def calculate_health_score(user_id: int) -> dict:
    """
    Calculate the complete Financial Health Score for a user.

    Uses the last 6 months of transaction data. Returns a dictionary
    containing the overall score, all four sub-scores, their raw values,
    and metadata about data availability.

    Returns:
        {
            overall_score:          float  0–100
            savings_rate_score:     float  0–100
            emergency_fund_score:   float  0–100
            consistency_score:      float  0–100
            commitment_score:       float  0–100
            savings_rate_pct:       float  raw savings rate %
            emergency_fund_months:  float  months of expenses covered
            spending_cv:            float  coefficient of variation
            commitment_rate_pct:    float  % of income committed to investment
            months_of_data:         int    number of months with transactions
            has_sufficient_data:    bool   True if >= 2 months available
        }
    """
    summaries     = get_monthly_summaries_range(user_id, months=6)
    active_months = [s for s in summaries if s["total_income"] > 0 or s["total_expenses"] > 0]
    income_months = [s for s in active_months if s["total_income"] > 0]
    months_of_data = len(active_months)

    # No income recorded at all — return zeroed result with a flag
    if not income_months:
        return {
            "overall_score": 0.0,
            "savings_rate_score": 0.0,
            "emergency_fund_score": 0.0,
            "consistency_score": 0.0,
            "commitment_score": 0.0,
            "savings_rate_pct": 0.0,
            "emergency_fund_months": 0.0,
            "spending_cv": 0.0,
            "commitment_rate_pct": 0.0,
            "months_of_data": months_of_data,
            "has_sufficient_data": False,
        }

    # ── 1. SAVINGS RATE ───────────────────────────────────────────────────────
    # Average net savings rate across all months that have income data
    savings_rates = []
    for s in income_months:
        rate = (s["net"] / s["total_income"]) * 100
        savings_rates.append(rate)

    avg_savings_rate = statistics.mean(savings_rates)

    # ── 2. EMERGENCY FUND ─────────────────────────────────────────────────────
    # Current liquid balance ÷ average monthly expenses
    current_balance = get_current_balance(user_id)

    expense_months = [s for s in active_months if s["total_expenses"] > 0]
    if expense_months:
        avg_monthly_expenses = statistics.mean([s["total_expenses"] for s in expense_months])
    else:
        avg_monthly_expenses = 0.0

    emergency_fund_months = (
        current_balance / avg_monthly_expenses
        if avg_monthly_expenses > 0 else 0.0
    )

    # ── 3. SPENDING CONSISTENCY ───────────────────────────────────────────────
    # Coefficient of variation of monthly expense totals
    expense_values = [s["total_expenses"] for s in active_months if s["total_expenses"] > 0]

    if len(expense_values) >= 2:
        mean_exp  = statistics.mean(expense_values)
        stdev_exp = statistics.stdev(expense_values)
        spending_cv = stdev_exp / mean_exp if mean_exp > 0 else 0.0
    else:
        # Only one month — cannot measure variability, assume consistent
        spending_cv = 0.0

    # ── 4. INVESTMENT COMMITMENT ──────────────────────────────────────────────
    # savings_transfer transactions as % of total income
    total_income_all  = sum(s["total_income"] for s in income_months)
    total_committed   = sum(
        s["by_category"].get("savings_transfer", 0)
        for s in active_months
    )

    commitment_rate_pct = (
        (total_committed / total_income_all) * 100
        if total_income_all > 0 else 0.0
    )

    # ── DIMENSION SCORES ──────────────────────────────────────────────────────
    savings_rate_score   = _score_savings_rate(avg_savings_rate)
    emergency_fund_score = _score_emergency_fund(emergency_fund_months)
    consistency_score    = _score_spending_consistency(spending_cv)
    commitment_score     = _score_investment_commitment(commitment_rate_pct)

    # ── COMPOSITE SCORE ───────────────────────────────────────────────────────
    # Uses the module-level HEALTH_WEIGHTS — the same dict the Quick Assessment
    # imports, so the composite is identical in both contexts.
    overall_score = (
        savings_rate_score   * HEALTH_WEIGHTS["savings_rate"]   +
        emergency_fund_score * HEALTH_WEIGHTS["emergency_fund"] +
        consistency_score    * HEALTH_WEIGHTS["consistency"]    +
        commitment_score     * HEALTH_WEIGHTS["commitment"]
    )

    return {
        "overall_score":         round(overall_score, 1),
        "savings_rate_score":    round(savings_rate_score, 1),
        "emergency_fund_score":  round(emergency_fund_score, 1),
        "consistency_score":     round(consistency_score, 1),
        "commitment_score":      round(commitment_score, 1),
        "savings_rate_pct":      round(avg_savings_rate, 1),
        "emergency_fund_months": round(emergency_fund_months, 1),
        "spending_cv":           round(spending_cv, 3),
        "commitment_rate_pct":   round(commitment_rate_pct, 1),
        "months_of_data":        months_of_data,
        "has_sufficient_data":   months_of_data >= 2,
    }
