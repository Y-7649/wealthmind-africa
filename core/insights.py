"""
core/insights.py
Cross-Module Insights Engine

The central analytical layer of WealthMind Africa.

Connects findings across all five modules — present bias detection,
financial health score, Kenya inflation context, and wealth projection
— to generate integrated economic insights that no single module
can produce in isolation.

Design principles:
    1. Each insight bridges at least two modules.
    2. Every insight follows a four-part structure:
           Observed  → what the data actually shows
           Concept   → the named economic theory behind it
           Why       → why this matters to the user's outcomes
           Impact    → quantified consequence where data allows
    3. Insights are ranked by severity so the most urgent signals
       appear first.
    4. Insights are suppressed (return None) when there is insufficient
       data to support them — a partial insight is worse than none.

Severity levels:
    critical → immediate financial vulnerability
    warning  → behavioural or structural drag on outcomes
    positive → a genuine financial strength worth naming
    info     → factual context that improves financial literacy

Academic foundations integrated here:
    - Laibson (1997) — present bias and its wealth consequences
    - O'Donoghue & Rabin (1999) — under-saving via hyperbolic discounting
    - Friedman (1957) — Permanent Income Hypothesis savings benchmark
    - Deaton (1991) — buffer stock saving and financial resilience
    - Hall (1978) — consumption smoothing and spending consistency
    - Fisher equation — real vs nominal wealth under inflation
"""

from core.health_score import calculate_health_score
from core.present_bias import calculate_present_bias
from core.projection   import get_projection_data, compound_growth, NOMINAL_RETURN_RATE

# ── SEVERITY ORDERING ─────────────────────────────────────────────────────────
# Controls the sort order: critical issues surface first.
_SEVERITY_ORDER = {"critical": 0, "warning": 1, "positive": 2, "info": 3}


def generate_insights(user_id: int, currency: str = "KES") -> list[dict]:
    """
    Generate all cross-module insights for a user.

    Calls each module's core engine, then runs six insight generators
    that each connect findings across at least two modules.

    Arguments:
        user_id:  The logged-in user's database ID
        currency: Display currency string (e.g. "KES")

    Returns:
        A list of insight dicts, sorted by severity (critical first).
        Empty list if there is not enough data for any insight.

        Each dict contains:
            title:            str  — short descriptive title
            icon:             str  — single emoji
            severity:         str  — "critical", "warning", "positive", or "info"
            observed:         str  — what the data shows
            concept:          str  — the economic theory behind it
            why:              str  — why it matters to the user's outcomes
            impact:           str  — quantified consequence (empty string if N/A)
            impact_positive:  bool — True if the impact message is good news
            module_link:      str  — page path for "Go deeper" link (or None)
    """
    # ── COLLECT DATA FROM ALL RELEVANT MODULES ────────────────────────────────
    health = calculate_health_score(user_id)
    bias   = calculate_present_bias(user_id, currency=currency)
    proj   = get_projection_data(user_id)

    # Run every generator; suppress None results (insufficient data)
    raw = [
        _bias_wealth_cost(bias, proj, currency),
        _savings_rate(health, proj, currency),
        _inflation_erosion(proj, currency),
        _emergency_fund(health, proj, currency),
        _spending_consistency(health, bias),
        _combined_behavioral(health, bias, proj, currency),
    ]

    insights = [i for i in raw if i is not None]

    # Sort: critical → warning → positive → info
    insights.sort(key=lambda x: _SEVERITY_ORDER.get(x["severity"], 99))
    return insights


# ── PRIVATE HELPERS ───────────────────────────────────────────────────────────

def _fv_20yr(monthly_amount: float, annual_rate: float) -> float:
    """
    Future value of a monthly contribution over 20 years at a given rate.
    Uses the same compound_growth formula as the Wealth Projection module
    so all quantified impacts are internally consistent.
    """
    if monthly_amount <= 0:
        return 0.0
    return compound_growth(
        principal=0.0,
        monthly_contribution=monthly_amount,
        annual_rate=annual_rate,
        years=20,
    )[-1]


# ── INSIGHT 1: Present Bias → Wealth Opportunity Cost ────────────────────────

def _bias_wealth_cost(bias: dict, proj: dict, currency: str) -> dict | None:
    """
    Connects: Present Bias module → Wealth Projection module.

    Translates the monthly cost of hyperbolic discounting into a 20-year
    future value — making the long-run consequence of the behavioural
    pattern visible and quantifiable.
    """
    if not bias.get("has_data"):
        return None

    index = bias["bias_index"]
    cost  = bias["implied_monthly_bias_cost"]
    label = bias["bias_label"]

    # Only generate this insight if there is a meaningful bias signal and cost
    if index < 1.1 or cost <= 0:
        return None

    rate = (
        proj.get("return_rate", NOMINAL_RETURN_RATE)
        if proj.get("has_data") else NOMINAL_RETURN_RATE
    )
    fv = _fv_20yr(cost, rate)

    severity = "warning" if index >= 1.3 else "info"

    return {
        "title":           "Present Bias Is Costing Future Wealth",
        "icon":            "🧠",
        "severity":        severity,
        "observed":        (
            f"Your spending data reveals {label.lower()} "
            f"(index: {index:.2f}). You spend {index:.2f}× more in Week 1 "
            f"than Week 4 each month — approximately {currency} {cost:,.0f} "
            f"above a uniform spending baseline per month."
        ),
        "concept":         (
            "Hyperbolic discounting (Laibson, 1997): people are disproportionately "
            "impatient in the short run, placing extra weight on immediate spending. "
            "This creates a predictable first-week spending surge after income "
            "arrives — a departure from the time-consistent, rational ideal."
        ),
        "why":             (
            f"Every {currency} spent above baseline due to present bias is a "
            f"{currency} not saved and not compounding. The pattern costs little "
            f"in any single month, but the absence of compound growth on that "
            f"money accumulates into a significant long-run wealth penalty."
        ),
        "impact":          (
            f"If the {currency} {cost:,.0f}/month excess were redirected to savings "
            f"at a {rate*100:.0f}% annual return (assumed — not a prediction), "
            f"it would compound to {currency} {fv:,.0f} over 20 years."
        ),
        "impact_positive": False,
        "module_link":     "pages/5_behaviour.py",
    }


# ── INSIGHT 2: Savings Rate → PIH Benchmark + 25-Year Projection Gap ─────────

def _savings_rate(health: dict, proj: dict, currency: str) -> dict | None:
    """
    Connects: Financial Health Score module → Wealth Projection module.

    Compares the user's actual savings rate to the Permanent Income
    Hypothesis benchmark, and quantifies the 25-year wealth gap between
    the current path and the +5pp improved path.
    """
    if not health.get("has_sufficient_data") or not proj.get("has_data"):
        return None

    rate    = health["savings_rate_pct"]
    gap_25  = (
        proj["at_25_years"]["improved"] - proj["at_25_years"]["current"]
        if proj.get("at_25_years") else 0.0
    )
    ret = proj.get("return_rate", NOMINAL_RETURN_RATE)

    # Above benchmark → positive signal
    if rate >= 20:
        return {
            "title":           f"Savings Rate {rate:.1f}% — Meets the PIH Benchmark",
            "icon":            "📊",
            "severity":        "positive",
            "observed":        (
                f"Your average savings rate over the last 6 months is {rate:.1f}%, "
                f"meeting the 20% Permanent Income Hypothesis benchmark."
            ),
            "concept":         (
                "Friedman's Permanent Income Hypothesis (1957): rational households "
                "save a stable fraction of their permanent income. The 20% benchmark "
                "is the widely-cited threshold in financial planning research."
            ),
            "why":             (
                "Consistently saving above 20% simultaneously builds compound returns "
                "and protects against income shocks. Maintaining this discipline "
                "over time is the single most powerful lever for long-run wealth "
                "accumulation available to an individual."
            ),
            "impact":          (
                f"At your current savings rate, your projected net worth in 25 years "
                f"is {currency} {proj['at_25_years']['current']:,.0f} "
                f"(assumed {ret*100:.0f}% annual return — not a prediction)."
            ),
            "impact_positive": True,
            "module_link":     "pages/2_health_score.py",
        }

    # Below benchmark → warning or critical
    severity = "critical" if rate < 10 else "warning"
    gap_pct  = 20.0 - rate

    return {
        "title":           f"Savings Rate {rate:.1f}% — Below the 20% PIH Benchmark",
        "icon":            "📊",
        "severity":        severity,
        "observed":        (
            f"Your average savings rate is {rate:.1f}%, which is "
            f"{gap_pct:.1f} percentage points below the 20% benchmark "
            f"from Friedman's Permanent Income Hypothesis."
        ),
        "concept":         (
            "Friedman's Permanent Income Hypothesis (1957): rational households "
            "save a stable fraction of permanent income. The 20% benchmark "
            "represents the minimum needed for meaningful capital accumulation "
            "and resilience against income shocks."
        ),
        "why":             (
            "The gap between your actual savings rate and 20% does not just "
            "represent money not saved today — it represents the compound growth "
            "destroyed by the absence of that capital over decades. Small "
            "percentage-point differences in savings rates produce very large "
            "long-run wealth gaps."
        ),
        "impact":          (
            f"Increasing your savings rate by 5 percentage points would add "
            f"{currency} {gap_25:,.0f} to your projected net worth over 25 years "
            f"(assumed {ret*100:.0f}% annual return — not a prediction)."
        ) if gap_25 > 0 else "",
        "impact_positive": False,
        "module_link":     "pages/4_projection.py",
    }


# ── INSIGHT 3: Inflation → Real vs Nominal Wealth Erosion ────────────────────

def _inflation_erosion(proj: dict, currency: str) -> dict | None:
    """
    Connects: Kenya Inflation Context module → Wealth Projection module.

    Shows the Fisher-equation gap between the nominal 25-year projection
    and its real purchasing-power equivalent, making the silent cost of
    inflation visible in the user's own projection data.
    """
    if not proj.get("has_data"):
        return None

    nominal = proj["at_25_years"]["current"]
    real    = proj["at_25_years"]["real"]
    infl    = proj.get("inflation_rate", 0.04)

    if nominal <= 1:
        return None

    erosion_abs = nominal - real
    erosion_pct = (erosion_abs / nominal) * 100

    return {
        "title":           "Inflation Will Erode Your Nominal Wealth",
        "icon":            "🇰🇪",
        "severity":        "info",
        "observed":        (
            f"Kenya's current headline inflation is {infl*100:.1f}%. "
            f"Your 25-year nominal projection of {currency} {nominal:,.0f} "
            f"represents only {currency} {real:,.0f} in real (inflation-adjusted) "
            f"purchasing power — a gap driven entirely by price increases."
        ),
        "concept":         (
            "The Fisher equation (Irving Fisher, 1867–1947): "
            "real return = ((1 + nominal) / (1 + inflation)) − 1. "
            "Applied to wealth projections, nominal growth overstates "
            "the actual gain in purchasing power. Real wealth measures "
            "what your money can actually buy, not how many currency units "
            "you hold."
        ),
        "why":             (
            "Targeting a nominal wealth figure without adjusting for inflation "
            "produces false confidence. If Kenya's inflation averages 4% per year, "
            "a nominal 'KES 10 million' target in 25 years is worth substantially "
            "less in today's purchasing power. The real projection is the "
            "economically meaningful benchmark."
        ),
        "impact":          (
            f"At {infl*100:.1f}% annual inflation, approximately {erosion_pct:.0f}% "
            f"({currency} {erosion_abs:,.0f}) of your projected nominal gain "
            f"over 25 years is consumed by price increases. "
            f"The Inflation-Adjusted scenario on the Wealth Projection page "
            f"shows your real purchasing power trajectory."
        ),
        "impact_positive": False,
        "module_link":     "pages/4_projection.py",
    }


# ── INSIGHT 4: Emergency Fund → Financial Resilience ─────────────────────────

def _emergency_fund(health: dict, proj: dict, currency: str) -> dict | None:
    """
    Connects: Financial Health Score module → Wealth Projection module.

    The emergency fund level determines both current resilience (health score)
    and starting principal for compound growth (projection). Both dimensions
    are addressed here.
    """
    if not health.get("has_sufficient_data"):
        return None

    months  = health["emergency_fund_months"]
    avg_exp = proj.get("avg_monthly_expenses", 0.0) if proj.get("has_data") else 0.0
    bal     = proj.get("current_balance",      0.0) if proj.get("has_data") else 0.0

    # Strong fund → positive signal
    if months >= 6:
        return {
            "title":           f"Strong Emergency Fund — {months:.1f} Months Covered",
            "icon":            "🛡️",
            "severity":        "positive",
            "observed":        (
                f"Your current balance covers {months:.1f} months of average "
                f"expenses, exceeding the 3–6 month buffer stock benchmark."
            ),
            "concept":         (
                "Buffer stock saving theory (Deaton, 1991): households accumulate "
                "a precautionary buffer to insulate consumption from income shocks, "
                "reducing reliance on costly credit during disruptions."
            ),
            "why":             (
                "A strong emergency fund prevents income shocks from forcing "
                "asset liquidation at the worst moment. It also provides the "
                "psychological security needed to stay committed to long-term "
                "investments without the temptation to withdraw when cash feels "
                "tight."
            ),
            "impact":          (
                f"Your starting balance ({currency} {bal:,.0f}) also serves as "
                f"the principal for compound growth. At 7% annual return "
                f"(assumed — not a prediction), this principal alone grows to "
                f"{currency} {bal * (1.07**25):,.0f} over 25 years without any "
                f"additional contributions."
            ) if bal > 0 else "",
            "impact_positive": True,
            "module_link":     "pages/2_health_score.py",
        }

    # Determine severity and describe shortfall
    if months < 1:
        severity = "critical"
        status   = "Critically Below"
        note     = (
            "You have less than one month of expenses in liquid savings, "
            "leaving you highly exposed to any income disruption."
        )
        target = 3
    elif months < 3:
        severity = "warning"
        status   = "Below"
        note     = f"You are {3 - months:.1f} months below the recommended 3-month minimum."
        target   = 3
    else:
        severity = "info"
        status   = "Approaching"
        note     = f"You are {6 - months:.1f} months below the strong 6-month benchmark."
        target   = 6

    shortfall = max((target - months) * avg_exp, 0) if avg_exp > 0 else 0

    return {
        "title":           f"Emergency Fund {status} the CBK Benchmark",
        "icon":            "🛡️",
        "severity":        severity,
        "observed":        (
            f"Your current balance covers {months:.1f} months of average expenses "
            f"({currency} {avg_exp:,.0f}/month). {note}"
        ),
        "concept":         (
            "Buffer stock saving theory (Deaton, 1991): rational households "
            "maintain a liquid buffer to avoid reducing consumption during income "
            "shocks. Without this buffer, a single disruption forces costly "
            "credit or premature asset liquidation, compounding the original shock."
        ),
        "why":             (
            "An emergency fund is not just a safety net — it is a compound "
            "growth protector. Without one, a job loss or unexpected expense "
            "interrupts your investment trajectory at exactly the wrong time. "
            "The CBK and most financial regulators recommend a minimum of "
            "3–6 months of expenses as a liquid buffer."
        ),
        "impact":          (
            f"Building to a {target}-month buffer requires approximately "
            f"{currency} {shortfall:,.0f} in additional savings "
            f"(based on {currency} {avg_exp:,.0f}/month average expenses)."
        ) if shortfall > 0 else "",
        "impact_positive": False,
        "module_link":     "pages/2_health_score.py",
    }


# ── INSIGHT 5: Spending Variability + Present Bias Interaction ────────────────

def _spending_consistency(health: dict, bias: dict) -> dict | None:
    """
    Connects: Financial Health Score (CV) → Present Bias (weekly pattern).

    When both the coefficient of variation and the bias index are elevated,
    it indicates two compounding behavioural forces that each independently
    reduce financial health and savings capacity.
    """
    if not health.get("has_sufficient_data"):
        return None

    cv    = health["spending_cv"]
    index = bias.get("bias_index", 1.0) if bias.get("has_data") else 1.0

    # Only generate this insight if there is a meaningful consistency signal
    if cv < 0.2:
        return None

    both_elevated = cv >= 0.3 and index >= 1.3
    severity      = "warning" if cv >= 0.3 else "info"
    cv_label      = "very high" if cv >= 0.5 else ("high" if cv >= 0.3 else "moderate")

    observed = (
        f"Your monthly expenses have {cv_label} variability "
        f"(coefficient of variation: {cv:.2f}). "
        + (
            f"Your present bias index is also elevated ({index:.2f}), "
            f"suggesting the two patterns are compounding simultaneously."
            if both_elevated else
            f"Under consumption smoothing theory, spending should remain "
            f"relatively stable relative to permanent income."
        )
    )

    why = (
        "High variability makes it structurally difficult to maintain a savings "
        "target — months with excessive spending deplete the buffer built up in "
        "leaner months. "
        + (
            "Combined with present bias, this creates a double drag: spending is "
            "both front-loaded within months AND highly variable across months, "
            "compressing your savings rate in two directions simultaneously."
            if both_elevated else
            "Identifying the source of variability — income shocks, irregular "
            "bills, or impulsive behaviour — is the first step to addressing it."
        )
    )

    return {
        "title":           "High Spending Variability Detected",
        "icon":            "📉",
        "severity":        severity,
        "observed":        observed,
        "concept":         (
            "Consumption smoothing (Hall, 1978): under the Permanent Income "
            "Hypothesis, rational agents smooth consumption relative to permanent "
            "income, not transitory fluctuations. A high coefficient of variation "
            "indicates spending driven by short-term conditions rather than "
            "stable, planned financial behaviour."
        ),
        "why":             why,
        "impact":          (
            f"A spending CV of {cv:.2f} contributes to a consistency sub-score "
            f"of {health['consistency_score']:.0f}/100, which carries a 20% "
            f"weight in your overall Financial Health Score."
        ),
        "impact_positive": False,
        "module_link":     "pages/2_health_score.py",
    }


# ── INSIGHT 6: Combined Behavioural Drag → Commitment Mechanism ───────────────

def _combined_behavioral(health: dict, bias: dict, proj: dict, currency: str) -> dict | None:
    """
    Connects: Present Bias + Savings Rate + Projection.

    Activates only when both conditions hold:
        - Savings rate below 15% (structurally under-saving)
        - Bias index above 1.3 (measurable hyperbolic discounting)

    This combination is documented by O'Donoghue and Rabin (1999) as
    creating a self-reinforcing cycle that willpower alone cannot break.
    The recommended intervention — a commitment mechanism — addresses
    both problems simultaneously.
    """
    if not health.get("has_sufficient_data") or not bias.get("has_data"):
        return None

    rate  = health["savings_rate_pct"]
    index = bias["bias_index"]
    cost  = bias["implied_monthly_bias_cost"]

    # Only generate this insight when both signals exceed threshold
    if rate >= 15 or index < 1.3:
        return None

    # Calculate the combined monthly drag
    combined_loss = 0.0
    ret = NOMINAL_RETURN_RATE
    if proj.get("has_data"):
        ret = proj.get("return_rate", NOMINAL_RETURN_RATE)
        inc = proj.get("monthly_income", 0.0)
        if inc > 0:
            target    = inc * 0.20
            actual    = proj.get("monthly_savings", 0.0)
            shortfall = max(target - actual, 0.0)
            combined_loss = shortfall + cost

    fv       = _fv_20yr(combined_loss, ret)
    severity = "critical" if rate < 5 else "warning"

    return {
        "title":           "Present Bias + Low Savings: A Compounding Drag",
        "icon":            "⚠️",
        "severity":        severity,
        "observed":        (
            f"Two signals are simultaneously active: your savings rate is {rate:.1f}% "
            f"(below the 15% threshold) and your present bias index is {index:.2f} "
            f"(above 1.3 — indicating measurable hyperbolic discounting). "
            f"These forces compound each other."
        ),
        "concept":         (
            "O'Donoghue and Rabin (1999): even mild present bias causes systematic "
            "under-saving because the same bias that defers saving today applies "
            "again next month. The result is a persistent intention-action gap — "
            "plans to 'save more starting next month' that never materialise "
            "because the next month brings the same bias."
        ),
        "why":             (
            "You are not just saving below target — you are also spending above "
            "the uniform baseline early each month. Both forces reduce savings "
            "simultaneously. Research shows that commitment devices — automated "
            "transfers on payday, executed before discretionary spending begins "
            "— break this cycle by removing the decision from the "
            "present-biased moment entirely."
        ),
        "impact":          (
            f"The combined monthly drag (savings shortfall + present bias cost) "
            f"is approximately {currency} {combined_loss:,.0f}/month. "
            f"Redirected to savings at {ret*100:.0f}% annual return "
            f"(assumed — not a prediction), this compounds to "
            f"{currency} {fv:,.0f} over 20 years."
        ) if fv > 0 else "",
        "impact_positive": False,
        "module_link":     "pages/5_behaviour.py",
    }
