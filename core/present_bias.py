"""
core/present_bias.py
Present Bias Detection Engine

Detects hyperbolic discounting in spending behaviour by analysing whether
discretionary spending is disproportionately concentrated at the start
of the month — immediately after income is received.

Academic foundation:
    Laibson, D. (1997). Golden Eggs and Hyperbolic Discounting.
    Quarterly Journal of Economics, 112(2), 443–478.

    O'Donoghue, T. & Rabin, M. (1999). Doing It Now or Later.
    American Economic Review, 89(1), 103–124.

    Deaton, A. (1991). Saving and Liquidity Constraints.
    Econometrica, 59(5), 1221–1248.

The theory:
    Standard economic models assume exponential discounting — people
    discount future rewards at a constant rate. Behavioural economics
    shows that people actually use hyperbolic discounting: they are
    very impatient in the short run but more patient in the long run.

    In spending behaviour, this creates a predictable weekly pattern:
    spending is highest immediately after income arrives (when money
    feels most "present") and lowest at the end of the month.

The measurement:
    Present Bias Index = Average Week 1 spending ÷ Average Week 4 spending

    Index > 1.3: Moderate present bias detected
    Index > 1.6: Strong present bias detected
    Index ≈ 1.0: No detectable bias
    Index < 0.8: Reverse pattern (unusual)

Why discretionary categories only:
    Fixed obligations (rent, utilities, education, health) are paid when
    they are due — not when the person feels like paying them. Including
    them would mask the discretionary spending signal we are looking for.
"""

from datetime import datetime
from database.db import get_weekly_spending


# ── BIAS CLASSIFICATION ───────────────────────────────────────────────────────

def _classify_bias(index: float) -> tuple[str, str]:
    """
    Classify the bias index into a human-readable label and a display colour.
    Returns (label, hex_colour).
    """
    if index >= 1.6:
        return "Strong Present Bias",   "#FF4444"
    elif index >= 1.3:
        return "Moderate Present Bias", "#FF8800"
    elif index >= 1.1:
        return "Mild Present Bias",     "#FFCC00"
    elif index >= 0.9:
        return "No Detectable Bias",    "#00C49F"
    else:
        return "Reverse Pattern",       "#8888FF"


# Public alias — the canonical bias classifier, shared with core/assessment.py
# so the Quick Assessment labels present bias identically to the tracker.
classify_bias = _classify_bias


# ── MAIN CALCULATION FUNCTION ─────────────────────────────────────────────────

def calculate_present_bias(user_id: int, currency: str = "KES") -> dict:
    """
    Calculate the present bias index from the last 3 months of data.

    Multiple months are used to average out noise — a single anomalous
    month (e.g. a large purchase in week 3) would distort a single-month
    reading. Three months produces a more statistically stable estimate.

    Returns:
        {
            has_data:                  bool
            has_sufficient_data:       bool  (True if >= 2 months)
            months_analysed:           int
            bias_index:                float
            bias_label:                str
            bias_colour:               str   (hex colour)
            weekly_averages:           dict  {week_1..week_4: float}
            monthly_breakdown:         list  per-month weekly figures
            implied_monthly_bias_cost: float KES excess vs. uniform baseline
            interpretation:            str   plain-English explanation
        }
    """
    now          = datetime.now()
    monthly_data = []

    # Collect weekly discretionary spending for the last 3 months
    for i in range(2, -1, -1):
        target_month = now.month - i
        target_year  = now.year

        # Handle year boundary (e.g. January - 1 = December of prior year)
        while target_month <= 0:
            target_month += 12
            target_year  -= 1

        weekly = get_weekly_spending(user_id, target_year, target_month)
        total  = sum(weekly.values())

        if total > 0:
            monthly_data.append({
                "label":  f"{target_year}-{target_month:02d}",
                "week_1": weekly["week_1"],
                "week_2": weekly["week_2"],
                "week_3": weekly["week_3"],
                "week_4": weekly["week_4"],
                "total":  total,
            })

    months_analysed = len(monthly_data)

    if months_analysed < 1:
        return {
            "has_data":        False,
            "months_analysed": 0,
        }

    # ── WEEKLY AVERAGES ───────────────────────────────────────────────────────
    avg_week = {}
    for week in ["week_1", "week_2", "week_3", "week_4"]:
        avg_week[week] = sum(m[week] for m in monthly_data) / months_analysed

    # ── PRESENT BIAS INDEX ────────────────────────────────────────────────────
    # Capped at 3.0: once week-1 spending is 3× week-4 the bias is already
    # "strong" (the classification tops out at 1.6), and an uncapped ratio
    # explodes to meaningless magnitudes when week-4 spending is near zero.
    _BIAS_CAP = 3.0
    if avg_week["week_4"] > 0:
        bias_index = min(avg_week["week_1"] / avg_week["week_4"], _BIAS_CAP)
    elif avg_week["week_1"] > 0:
        bias_index = _BIAS_CAP   # Week 4 is zero — strong bias, capped for display
    else:
        bias_index = 1.0   # No data in either week

    bias_label, bias_colour = _classify_bias(bias_index)

    # ── ESTIMATED COST OF BIAS ────────────────────────────────────────────────
    # If spending were uniform, each week would be exactly 25% of the monthly
    # total. The "cost" of present bias is the excess Week 1 spending above
    # that uniform baseline — money spent due to impatience rather than need.
    avg_monthly_total = sum(m["total"] for m in monthly_data) / months_analysed
    uniform_week      = avg_monthly_total / 4
    week1_excess      = max(avg_week["week_1"] - uniform_week, 0)

    interpretation = _generate_interpretation(bias_index, bias_label, avg_week, week1_excess, currency)

    return {
        "has_data":                  True,
        "has_sufficient_data":       months_analysed >= 2,
        "months_analysed":           months_analysed,
        "bias_index":                round(bias_index, 2),
        "bias_label":                bias_label,
        "bias_colour":               bias_colour,
        "weekly_averages":           {k: round(v, 2) for k, v in avg_week.items()},
        "monthly_breakdown":         monthly_data,
        "implied_monthly_bias_cost": round(week1_excess, 2),
        "interpretation":            interpretation,
    }


def _generate_interpretation(
    index: float,
    label: str,
    avg_week: dict,
    excess: float,
    currency: str = "KES",
) -> str:
    """
    Generate a plain-English interpretation that connects the data
    to the academic concept of hyperbolic discounting.
    """
    if index >= 1.3:
        return (
            f"Your data shows {label.lower()} — you spend approximately "
            f"{index:.2f}× more in the first week of the month than the last. "
            f"This is consistent with hyperbolic discounting: money feels most "
            f"'present' immediately after it arrives, making early spending "
            f"more tempting. Laibson (1997) identifies this as one of the most "
            f"common and costly departures from rational financial behaviour. "
            f"Based on your data, this pattern costs an estimated "
            f"{currency} {excess:,.0f} per month in above-baseline early spending."
        )
    elif index >= 1.1:
        return (
            f"Your data shows mild present bias — first-week spending is "
            f"{index:.2f}× your last-week spending on average. This is a "
            f"moderate form of hyperbolic discounting that is very common, "
            f"particularly among young adults. Awareness of this pattern "
            f"is the first step toward addressing it."
        )
    elif index >= 0.9:
        return (
            f"Your spending is distributed fairly evenly across the month "
            f"(bias index: {index:.2f}). No significant present bias is "
            f"detectable in your data. This is consistent with time-consistent "
            f"preferences and rational consumption smoothing — a positive "
            f"finding from a behavioural economics perspective."
        )
    else:
        return (
            f"Your spending is actually higher at the end of the month than "
            f"the beginning (index: {index:.2f}). This reverse pattern is "
            f"unusual and may reflect deferred billing cycles or deliberate "
            f"end-of-month spending habits rather than a behavioural bias."
        )
