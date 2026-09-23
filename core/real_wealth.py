"""
core/real_wealth.py
WealthMind Africa — Real vs Nominal Wealth Engine (Version 1.1)

Answers one question:

    "Did your money actually become more valuable,
     or did it just become a bigger number?"

Pure functions only — no Streamlit, no database, no I/O — so the maths is fully
unit-testable and reproducible. This module is a NEW Version 1.1 educational
feature. It introduces NO new health/behaviour score and never touches the
Version 1.0 assessment engine (core/assessment.py, core/health_score.py,
core/present_bias.py). Nothing here is stored against a participant's score.

The mathematics is the Fisher relation between nominal and real growth:

    real_growth_factor = (1 + nominal) / (1 + inflation)

Over n periods this compounds:

    real_return_total = ((1 + g) / (1 + i)) ** n − 1

which is why the real return is NOT simply (g − i). Subtracting the two rates
ignores that inflation compounds on top of the nominal gain. For a single period
the two are close; over many years they diverge materially. Example:

    g = 10%, i = 6%  →  real ≈ (1.10 / 1.06) − 1 = 3.77%  (not 4%)
"""

from dataclasses import dataclass


# ── RESULT CONTAINER ──────────────────────────────────────────────────────────

@dataclass
class RealWealthResult:
    """The full nominal-vs-real breakdown for one scenario."""
    start:                        float   # starting amount
    years:                        int     # whole-year horizon
    annual_growth:                float   # decimal, e.g. 0.10 = 10%
    annual_inflation:             float   # decimal, e.g. 0.06 = 6%

    nominal_value:                float   # future amount in future shillings
    real_value:                   float   # future amount in TODAY's shillings

    nominal_return_total:         float   # (1+g)^n − 1        (whole horizon)
    real_return_total:            float   # ((1+g)/(1+i))^n − 1 (whole horizon)
    nominal_return_annual:        float   # g                  (per year)
    real_return_annual:           float   # (1+g)/(1+i) − 1    (per year, Fisher)

    purchasing_power_change:      float   # == real_return_total (of the invested sum)
    cash_purchasing_power_change: float   # 1/(1+i)^n − 1  (if left as idle cash)

    series:                       list    # [{"year", "nominal", "real"}], y = 0..n


# ── CORE MATHS ────────────────────────────────────────────────────────────────

def real_growth_annual(annual_growth: float, annual_inflation: float) -> float:
    """
    The one-year REAL growth rate via the Fisher relation.

    real = (1 + nominal) / (1 + inflation) − 1

    This is deliberately NOT (nominal − inflation): subtracting the rates
    understates the erosion because inflation applies to the grown amount,
    not just the original.
    """
    return (1.0 + annual_growth) / (1.0 + annual_inflation) - 1.0


def project_real_wealth(start, annual_growth, annual_inflation, years) -> RealWealthResult:
    """
    Project nominal and inflation-adjusted (real) wealth over `years`.

    Arguments (plain numbers, rates as decimals):
        start:            starting amount (>= 0)
        annual_growth:    expected nominal annual growth  (0.10 = 10%)
        annual_inflation: assumed annual inflation        (0.06 = 6%)
        years:            whole number of years (>= 0)

    Edge cases are handled defensively so the UI can never crash on odd input:
        - start < 0            → treated as 0
        - years < 0            → treated as 0 (values collapse to `start`)
        - inflation <= −100%   → clamped just above −1 to avoid divide-by-zero

    Returns a RealWealthResult. `real_value` is the future nominal amount
    expressed in today's purchasing power; `real_return_total` /
    `purchasing_power_change` are the honest "are you actually better off?" figure.
    """
    start = max(0.0, float(start))
    years = max(0, int(years))
    g = float(annual_growth)
    i = float(annual_inflation)

    # Guard the denominator (1 + i). Inflation of −100% or worse is nonsensical
    # and would divide by zero / go negative.
    if i <= -0.9999:
        i = -0.9999

    growth_factor    = (1.0 + g) ** years
    inflation_factor = (1.0 + i) ** years

    nominal_value = start * growth_factor
    real_value    = nominal_value / inflation_factor

    nominal_return_total = growth_factor - 1.0
    real_return_total    = (growth_factor / inflation_factor) - 1.0

    # Year-by-year series for the diverging nominal-vs-real chart.
    series = []
    for y in range(years + 1):
        gf  = (1.0 + g) ** y
        inf = (1.0 + i) ** y
        nominal_y = start * gf
        series.append({
            "year":    y,
            "nominal": nominal_y,
            "real":    nominal_y / inf,
        })

    return RealWealthResult(
        start=start,
        years=years,
        annual_growth=g,
        annual_inflation=i,
        nominal_value=nominal_value,
        real_value=real_value,
        nominal_return_total=nominal_return_total,
        real_return_total=real_return_total,
        nominal_return_annual=g,
        real_return_annual=real_growth_annual(g, i),
        purchasing_power_change=real_return_total,
        cash_purchasing_power_change=(1.0 / inflation_factor) - 1.0,
        series=series,
    )


def plain_verdict(result: RealWealthResult, currency: str = "KES") -> str:
    """
    A one-sentence, no-jargon interpretation of the result — the sentence a
    person with no economics background should understand in seconds.
    """
    n_pct = result.nominal_return_total * 100
    r_pct = result.real_return_total * 100
    cur = currency

    if result.years == 0 or result.start == 0:
        return "Enter an amount and a time horizon to see how inflation reshapes it."

    if r_pct > 0.05:
        return (
            f"Your {cur} {result.start:,.0f} grows to {cur} {result.nominal_value:,.0f} "
            f"on paper (+{n_pct:.0f}%), but in today's money it's really worth "
            f"{cur} {result.real_value:,.0f}. You're genuinely about {r_pct:.0f}% "
            f"better off — not {n_pct:.0f}%."
        )
    if r_pct < -0.05:
        return (
            f"Your {cur} {result.start:,.0f} grows to {cur} {result.nominal_value:,.0f} "
            f"on paper (+{n_pct:.0f}%), but inflation outpaces it: in today's money "
            f"it's worth only {cur} {result.real_value:,.0f}. Your purchasing power "
            f"actually falls about {abs(r_pct):.0f}%."
        )
    return (
        f"Your {cur} {result.start:,.0f} grows to {cur} {result.nominal_value:,.0f} "
        f"on paper, but after inflation your purchasing power is essentially "
        f"unchanged — a bigger number, not more real wealth."
    )
