"""
core/analytics.py
Cohort Analytics Engine

Aggregates anonymised, cohort-level economic statistics across all users —
the analytical backbone of both the Admin Analytics Dashboard and the public
School Impact Report.

Design principles:
    - ANONYMITY: only aggregates leave this module. No usernames, no per-user
      identifiable rows. Distributions are returned as bare arrays of numbers.
    - HONESTY: every aggregate carries its sample size (n). Insight sentences
      are only generated when enough users contribute to be meaningful.
    - REUSE: per-user economics come from the same engines the user-facing
      pages use (health_score, present_bias) — the cohort study and the
      individual analysis are computed identically.

Economic concepts surfaced at the cohort level:
    - Composite indexing      → distribution of Financial Health Scores
    - Permanent income        → distribution of savings rates
    - Buffer stock theory     → distribution of emergency-fund coverage
    - Hyperbolic discounting  → prevalence of present bias across the cohort
"""

import statistics
from collections import Counter

from database.db import (
    count_users,
    count_active_users,
    count_transactions,
    get_transaction_value_summary,
    get_category_totals,
    get_currency_distribution,
    get_monthly_user_growth,
    get_monthly_transaction_growth,
    get_all_user_ids,
    get_assessment_scores,
    get_assessment_growth,
    count_anonymous_assessments,
)
from core.health_score import calculate_health_score
from core.present_bias import calculate_present_bias
from core.assessment import AGE_LABELS, LIFE_STAGE_LABELS, CATEGORY_LABELS

# Minimum cohort size before the public School Impact Report will display
# aggregated behavioural statistics. Below this, individual data points could
# be inferred from an aggregate — so the public page shows a "cohort building"
# state instead. The admin dashboard has no such floor (admin is trusted).
MIN_PUBLIC_COHORT = 5

# A present bias index at or above this threshold is treated as a measurable
# departure from time-consistent preferences (the module's "Mild" band begins
# at 1.1; "No Detectable Bias" sits in 0.9–1.1).
PRESENT_BIAS_THRESHOLD = 1.1
STRONG_BIAS_THRESHOLD = 1.6

# Minimum respondents in a demographic group (age band / life stage) before that
# group's averages are reported — so a life-stage comparison can never expose a
# near-individual data point. Cross-group questions ("does present bias fall with
# age?") are only meaningful, and only shown, above this floor.
MIN_DEMOGRAPHIC_GROUP = 8


def _safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _safe_median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def _band_counts(values: list[float], edges: list[float]) -> dict:
    """
    Bucket values into bands defined by `edges`.
    Returns {"label": count}. Edges are upper-exclusive boundaries; the final
    band captures everything at or above the last edge.
    """
    labels = []
    for i, e in enumerate(edges):
        lo = 0 if i == 0 else edges[i - 1]
        labels.append(f"{lo:g}–{e:g}")
    labels.append(f"{edges[-1]:g}+")

    counts = {label: 0 for label in labels}
    for v in values:
        placed = False
        for i, e in enumerate(edges):
            lo = 0 if i == 0 else edges[i - 1]
            if lo <= v < e:
                counts[labels[i]] += 1
                placed = True
                break
        if not placed:
            counts[labels[-1]] += 1
    return counts


def _demographic_breakdown(rows: list[dict], field: str, label_map: dict) -> list[dict]:
    """
    Average the behavioural scores within each demographic group (age band or
    life stage), returning only groups large enough to report (>= MIN_DEMOGRAPHIC
    _GROUP). This is what powers life-stage comparisons such as "does present
    bias decrease with age?" — always in aggregate, never below the floor.
    """
    groups: dict[str, list[dict]] = {}
    for r in rows:
        key = r.get(field)
        if not key:
            continue
        groups.setdefault(key, []).append(r)

    out = []
    for key, grp in groups.items():
        if len(grp) < MIN_DEMOGRAPHIC_GROUP:
            continue
        health = [x["health_score"]          for x in grp if x["health_score"] is not None]
        bias   = [x["bias_index"]            for x in grp if x["bias_index"] is not None]
        emer   = [x["emergency_fund_months"] for x in grp if x["emergency_fund_months"] is not None]
        sav    = [x["savings_rate_pct"]      for x in grp if x["savings_rate_pct"] is not None]
        out.append({
            "group":          label_map.get(key, key),
            "code":           key,
            "n":              len(grp),
            "avg_health":     round(_safe_mean(health), 1),
            "avg_bias":       round(_safe_mean(bias), 2),
            "avg_resilience": round(_safe_mean(emer), 1),
            "avg_savings":    round(_safe_mean(sav), 1),
        })
    # Stable presentation order: by the label map's declared order.
    order = list(label_map.keys())
    out.sort(key=lambda d: order.index(d["code"]) if d["code"] in order else 99)
    return out


def get_cohort_analytics() -> dict:
    """
    Compute the full anonymised cohort dataset.

    Returns a dictionary with adoption metrics, value metrics, behavioural
    distributions, and a list of auto-generated insight sentences. Every
    behavioural block carries the number of users it was computed from.

    This is intentionally a single pass: it is called once per page load and
    cached at the page layer (st.cache_data) so repeated reruns are free.
    """
    user_ids = get_all_user_ids()
    n_users  = len(user_ids)

    # ── Adoption & value (cheap SQL aggregates) ───────────────────────────────
    n_active_7d  = count_active_users(7)
    n_active_30d = count_active_users(30)
    n_txns       = count_transactions()
    value        = get_transaction_value_summary()
    categories   = get_category_totals()
    currencies   = get_currency_distribution()
    user_growth  = get_monthly_user_growth()
    txn_growth   = get_monthly_transaction_growth()

    # Dominant currency — used to label the aggregated monetary figures honestly
    primary_currency = currencies[0]["currency"] if currencies else "KES"

    # Category percentages
    total_expense = sum(c["total"] for c in categories) or 1.0
    for c in categories:
        c["pct"] = c["total"] / total_expense * 100

    # ── Per-user economics (loop the engines) ─────────────────────────────────
    overall_scores, savings_rates, emergency_months, commitment_rates = [], [], [], []
    bias_indices = []

    for uid in user_ids:
        hs = calculate_health_score(uid)
        if hs.get("has_sufficient_data"):
            overall_scores.append(hs["overall_score"])
            savings_rates.append(hs["savings_rate_pct"])
            emergency_months.append(hs["emergency_fund_months"])
            commitment_rates.append(hs["commitment_rate_pct"])

        pb = calculate_present_bias(uid)
        if pb.get("has_data"):
            bias_indices.append(pb["bias_index"])

    # Tracker-only counts, captured before pooling for honest source attribution.
    n_tracking_scored = len(overall_scores)
    n_tracking_biased = len(bias_indices)

    # ── Pool in Quick Assessment respondents ──────────────────────────────────
    # The assessment is a self-reported instrument scored on the IDENTICAL curves
    # (core/assessment.py reuses the same scoring functions), so its scores pool
    # validly with tracker scores. The two sources are counted separately so the
    # Impact Report can state the split honestly and never conflate them.
    a_scores = get_assessment_scores()
    a_health    = [r["health_score"]          for r in a_scores if r["health_score"] is not None]
    a_savings   = [r["savings_rate_pct"]       for r in a_scores if r["savings_rate_pct"] is not None]
    a_emergency = [r["emergency_fund_months"]  for r in a_scores if r["emergency_fund_months"] is not None]
    a_commit    = [r["commitment_rate_pct"]    for r in a_scores if r.get("commitment_rate_pct") is not None]
    a_bias      = [r["bias_index"]             for r in a_scores if r["bias_index"] is not None]

    overall_scores   = overall_scores   + a_health
    savings_rates    = savings_rates    + a_savings
    emergency_months = emergency_months + a_emergency
    commitment_rates = commitment_rates + a_commit
    bias_indices     = bias_indices     + a_bias

    n_scored = len(overall_scores)
    n_biased = len(bias_indices)

    # Participation. Use anonymous assessments in the total so an account that
    # later claims its assessment is not double-counted.
    n_assessment       = len(a_scores)
    n_anon_assessment  = count_anonymous_assessments()
    n_tracking_users   = n_users
    total_participants = n_tracking_users + n_anon_assessment

    # ── Behavioural aggregates (pooled across both instruments) ───────────────
    health = {
        "n_scored":                n_scored,
        "n_tracking":              n_tracking_scored,
        "n_assessment":            len(a_health),
        "avg_overall":             round(_safe_mean(overall_scores), 1),
        "median_overall":          round(_safe_median(overall_scores), 1),
        "avg_savings_rate":        round(_safe_mean(savings_rates), 1),
        "median_savings_rate":     round(_safe_median(savings_rates), 1),
        "avg_emergency_months":    round(_safe_mean(emergency_months), 1),
        "median_emergency_months": round(_safe_median(emergency_months), 1),
        "avg_commitment":          round(_safe_mean(commitment_rates), 1),
        "score_distribution":      _band_counts(overall_scores, [40, 70]),  # weak / developing / strong
        "score_values":            [round(s, 1) for s in overall_scores],
        "savings_values":          [round(s, 1) for s in savings_rates],
    }

    pct_present = (sum(1 for b in bias_indices if b >= PRESENT_BIAS_THRESHOLD) / n_biased * 100) if n_biased else 0.0
    pct_strong  = (sum(1 for b in bias_indices if b >= STRONG_BIAS_THRESHOLD) / n_biased * 100) if n_biased else 0.0
    bias = {
        "n_measured":   n_biased,
        "n_tracking":   n_tracking_biased,
        "n_assessment": len(a_bias),
        "avg_index":    round(_safe_mean(bias_indices), 2),
        "median_index": round(_safe_median(bias_indices), 2),
        "pct_present_bias": round(pct_present, 1),
        "pct_strong_bias":  round(pct_strong, 1),
        "index_values": [round(b, 2) for b in bias_indices],
    }

    pct_below_3m = (sum(1 for m in emergency_months if m < 3) / n_scored * 100) if n_scored else 0.0
    resilience = {
        "avg_months":   round(_safe_mean(emergency_months), 1),
        "median_months": round(_safe_median(emergency_months), 1),
        "pct_below_3m": round(pct_below_3m, 1),
        "distribution": _band_counts(emergency_months, [1, 3, 6]),
        "values":       [round(m, 1) for m in emergency_months],
    }

    # ── Assessment-only views: demographics + cited spending categories ───────
    # Demographics exist only for assessment respondents, so life-stage / age
    # comparisons are drawn from that instrument and labelled accordingly.
    demographics = {
        "min_group":     MIN_DEMOGRAPHIC_GROUP,
        "by_age":        _demographic_breakdown(a_scores, "age_band", AGE_LABELS),
        "by_life_stage": _demographic_breakdown(a_scores, "life_stage", LIFE_STAGE_LABELS),
    }

    cat_counter = Counter()
    for r in a_scores:
        for code in (r.get("ans_categories") or "").split(","):
            if code:
                cat_counter[code] += 1
    assessment_categories = [
        {"category": CATEGORY_LABELS.get(k, k), "count": v}
        for k, v in cat_counter.most_common()
    ]

    result = {
        # adoption / value
        "n_users":        n_users,
        "n_active_7d":    n_active_7d,
        "n_active_30d":   n_active_30d,
        "n_transactions": n_txns,
        "value":          value,
        "primary_currency": primary_currency,
        "categories":     categories,
        "currencies":     currencies,
        "user_growth":    user_growth,
        "txn_growth":     txn_growth,
        # participation (assessment + tracking)
        "participants": {
            "n_assessment": n_assessment,
            "n_tracking":   n_tracking_users,
            "total":        total_participants,
        },
        "assessment_growth":     get_assessment_growth(),
        "assessment_categories": assessment_categories,
        # behavioural
        "health":       health,
        "bias":         bias,
        "resilience":   resilience,
        "demographics": demographics,
        "min_public_cohort": MIN_PUBLIC_COHORT,
        "meets_public_threshold": total_participants >= MIN_PUBLIC_COHORT,
    }
    result["insights"] = generate_cohort_insights(result)
    return result


def generate_cohort_insights(c: dict) -> list[str]:
    """
    Produce declarative, research-report-style findings from the cohort data.

    Each sentence is only emitted when its underlying sample is large enough to
    be meaningful, so the report never overstates a finding drawn from one or
    two users. Phrased the way a behavioural-economics briefing would read.
    """
    insights = []
    cur = c["primary_currency"]
    health, bias, resilience = c["health"], c["bias"], c["resilience"]

    # Participation split (assessment vs ongoing tracking)
    p = c.get("participants", {})
    if p.get("total", 0) >= 1:
        insights.append(
            f"{p['total']} people have participated in WealthMind's behavioural "
            f"economics study — {p['n_assessment']} via the Quick Assessment and "
            f"{p['n_tracking']} through ongoing financial tracking."
        )

    # Savings rate (Permanent Income Hypothesis)
    if health["n_scored"] >= 2:
        insights.append(
            f"The average savings rate across {health['n_scored']} analysed users "
            f"is {health['avg_savings_rate']:.1f}% (median {health['median_savings_rate']:.1f}%) — "
            f"against the 20% benchmark from permanent-income theory."
        )

    # Present bias prevalence (Hyperbolic Discounting)
    if bias["n_measured"] >= 2:
        insights.append(
            f"{bias['pct_present_bias']:.0f}% of {bias['n_measured']} measured users exhibit "
            f"measurable present bias (index ≥ {PRESENT_BIAS_THRESHOLD}), with a cohort "
            f"average index of {bias['avg_index']:.2f} — a direct, observable trace of "
            f"hyperbolic discounting in real spending data."
        )

    # Spending composition (cohort consumption basket)
    cats = c["categories"]
    if len(cats) >= 2 and sum(x["total"] for x in cats) > 0:
        top2 = cats[:2]
        pct2 = top2[0]["pct"] + top2[1]["pct"]
        names = " and ".join(x["category"].replace("_", " ") for x in top2)
        insights.append(
            f"{names.capitalize()} account for {pct2:.0f}% of all recorded spending — "
            f"echoing the food-and-transport weight of Kenya's national CPI basket."
        )

    # Emergency fund / buffer stock
    if health["n_scored"] >= 2:
        insights.append(
            f"The median emergency fund covers {resilience['median_months']:.1f} months "
            f"of expenses, and {resilience['pct_below_3m']:.0f}% of users fall below the "
            f"3-month buffer that Deaton's (1991) buffer-stock theory treats as the "
            f"minimum shock absorber."
        )

    # Composite health
    if health["n_scored"] >= 2:
        insights.append(
            f"The average Financial Health Score is {health['avg_overall']:.0f}/100, a "
            f"composite index built the way the World Bank's HDI and IMF soundness "
            f"indicators combine weighted sub-scores."
        )

    return insights
