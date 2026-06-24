"""
core/assessment.py
WealthMind Africa — Financial Behaviour Assessment Engine

WealthMind is a behavioural economics platform studying financial
decision-making across different age groups and life stages. The Quick
Assessment is its primary research instrument: a two-minute, self-reported
questionnaire that produces the same four economic scores as the long-term
tracker — without requiring any transaction history.

────────────────────────────────────────────────────────────────────────────
ONE SOURCE OF TRUTH
This module performs NO scoring mathematics of its own. It maps a respondent's
self-reported answers to the SAME intermediate quantities the tracker derives
from transactions (savings rate, emergency-fund months, spending CV, investment
commitment rate, present-bias index), then applies the SHARED scoring functions
imported from core.health_score and core.present_bias. An assessment respondent
and a tracking user are therefore scored on identical curves.

NO synthetic transactions are ever created. The assessment writes one honest
record (see database.save_assessment) and nothing else.
────────────────────────────────────────────────────────────────────────────

Economic grounding of each scored question:
    Q2 Savings      → Permanent Income Hypothesis (Friedman, 1957)
    Q3 Commitment   → Capital accumulation (Solow)
    Q4 Buffer       → Buffer-stock saving theory (Deaton, 1991)
    Q5 Timing       → Hyperbolic discounting / present bias (Laibson, 1997)
    Q6 Consistency  → Consumption smoothing (Hall, 1978)
    Q8 Inflation    → Real vs nominal value (Fisher, 1930)  [insight only]
"""

from core.health_score import (
    score_savings_rate,
    score_emergency_fund,
    score_spending_consistency,
    score_investment_commitment,
    HEALTH_WEIGHTS,
)
from core.present_bias import classify_bias

# ── POSITIONING COPY (shared by the UI, results page, and reports) ────────────

ASSESSMENT_NAME = "WealthMind Quick Assessment"
ASSESSMENT_TAGLINE = (
    "A behavioural economics assessment studying financial decision-making "
    "across different age groups and life stages."
)
ASSESSMENT_INTRO = (
    "Discover how economic theory explains your financial behaviour "
    "in under two minutes."
)

# Cohort size required before "how you compare" feedback is shown on the
# results page. Below this, a comparison could expose near-individual data.
MIN_COHORT_FOR_COMPARISON = 10

# ── ANSWER → QUANTITY BAND MAPS ───────────────────────────────────────────────
# Band code → the economic quantity the tracker would have measured. Midpoints
# for ranges. These six maps are the ONLY new numbers the assessment introduces;
# everything downstream is the shared scoring code.

INCOME_BANDS = {           # KES per month (midpoint) — context/display only
    "i_u5":    3000,
    "i_5_15":  10000,
    "i_15_30": 22000,
    "i_30_60": 45000,
    "i_o60":   80000,
}

SAVINGS_RATE_BANDS = {     # % of income left at month end → savings rate
    "s_none":  -5.0,       # "nothing / I run short"
    "s_tenth": 10.0,
    "s_fifth": 20.0,
    "s_third": 33.0,
    "s_half":  50.0,
}

COMMITMENT_BANDS = {       # deliberate saving/investing as % of income
    "c_never":  0.0,
    "c_occ":    2.0,
    "c_little": 6.0,
    "c_set":    12.0,
}

BUFFER_MONTHS_BANDS = {    # months of expenses savings would cover
    "b_week":  0.2,
    "b_2week": 0.5,
    "b_1_2mo": 1.5,
    "b_3_6mo": 4.5,
    "b_6plus": 8.0,
}

TIMING_BIAS_BANDS = {      # spending timing → present-bias index (week1/week4)
    "t_after":  1.8,       # "mostly right after I get money"
    "t_even":   1.0,
    "t_end":    0.8,
    "t_unsure": 1.25,
}

CONSISTENCY_CV_BANDS = {   # month-to-month similarity → coefficient of variation
    "v_very":   0.07,
    "v_rough":  0.18,
    "v_varies": 0.38,
    "v_unpred": 0.60,
}

# Neutral fallbacks if an answer is somehow missing (the flow makes Q1–Q6
# required, but guarding keeps scoring robust).
_DEFAULTS = {
    "savings": ("s_none", -5.0),
    "commitment": ("c_never", 0.0),
    "buffer": ("b_2week", 0.5),
    "timing": ("t_unsure", 1.25),
    "consistency": ("v_rough", 0.18),
}

# ── DEMOGRAPHIC + CATEGORY LABELS (aggregate-only) ────────────────────────────

AGE_LABELS = {
    "u18": "Under 18", "18_24": "18–24", "25_34": "25–34",
    "35_49": "35–49", "50p": "50+",
}
LIFE_STAGE_LABELS = {
    "secondary": "Secondary school student",
    "university": "University student",
    "early_career": "Early career professional",
    "working": "Working professional",
    "self_employed": "Self-employed / business owner",
    "parent": "Parent / guardian",
    "retired": "Retired",
    "other": "Other",
}
GENDER_LABELS = {"male": "Male", "female": "Female", "prefer_not": "Prefer not to say"}
CATEGORY_LABELS = {
    "food": "Food", "transport": "Transport", "rent": "Rent / housing",
    "airtime": "Airtime / data", "going_out": "Going out",
    "education": "Education", "other": "Other",
}

# ── CURRENCY → INCOME-RANGE LABELS ────────────────────────────────────────────
# The currency a respondent picks ONLY changes the income ranges shown on the
# income question. The internal band codes (INCOME_CODES) and every scoring
# function stay identical — the engine is unit-free, so currency never affects
# any score.

INCOME_CODES = ["i_u5", "i_5_15", "i_15_30", "i_30_60", "i_o60"]

CURRENCY_LABELS = {
    "KES":   "🇰🇪 KES — Kenyan Shilling",
    "USD":   "🇺🇸 USD — US Dollar",
    "GBP":   "🇬🇧 GBP — British Pound",
    "EUR":   "🇪🇺 EUR — Euro",
    "INR":   "🇮🇳 INR — Indian Rupee",
    "Other": "🌍 Other",
}

CURRENCY_INCOME_LABELS = {
    "KES":   ["Under KES 5,000", "KES 5,000–15,000", "KES 15,000–30,000",
              "KES 30,000–60,000", "Above KES 60,000"],
    "USD":   ["Under $50", "$50–150", "$150–300", "$300–600", "Above $600"],
    "GBP":   ["Under £40", "£40–120", "£120–250", "£250–500", "Above £500"],
    "EUR":   ["Under €50", "€50–140", "€140–280", "€280–550", "Above €550"],
    "INR":   ["Under ₹4,000", "₹4,000–12,000", "₹12,000–25,000",
              "₹25,000–50,000", "Above ₹50,000"],
    "Other": ["Very low", "Low", "Moderate", "High", "Very high"],
}


def income_options(currency: str = "KES") -> list:
    """
    Return the income question's options for a given currency: the same band
    CODES (INCOME_CODES), only the displayed labels change. Scoring is unaffected.
    """
    labels = CURRENCY_INCOME_LABELS.get(currency, CURRENCY_INCOME_LABELS["Other"])
    return [{"code": code, "label": label} for code, label in zip(INCOME_CODES, labels)]


# ── RESULTS COPY (plain-English; educational, not jargon) ─────────────────────

SCORE_EXPLANATIONS = {
    "health":       "Your overall financial wellbeing score based on your saving, "
                    "spending, resilience, and planning habits.",
    "present_bias": "Present bias measures whether you focus more on today's spending "
                    "than future financial goals. Higher scores indicate stronger "
                    "long-term planning habits.",
    "consistency":  "Measures how predictable your spending habits are.",
    "savings":      "The percentage of your income that you regularly save.",
    "resilience":   "Measures how long you could support yourself if your income stopped.",
}


def band_label(score: float) -> str:
    """Map any 0–100 score to a simple, friendly band."""
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 40:
        return "Moderate"
    return "Developing"


# Verdict sentence fragments, keyed by behavioural dimension.
STRENGTH_PHRASES = {
    "savings":      "maintaining a healthy savings rate",
    "resilience":   "maintaining an emergency buffer",
    "consistency":  "keeping your spending consistent month to month",
    "commitment":   "regularly committing money to savings or investment",
    "present_bias": "resisting the pull to overspend right after income arrives",
}
OPPORTUNITY_PHRASES = {
    "savings":      "increasing how much of your income you save",
    "resilience":   "building a larger emergency buffer",
    "consistency":  "making your month-to-month spending more consistent",
    "commitment":   "setting money aside for savings or investment more regularly",
    "present_bias": "improving long-term planning by reducing present bias",
}


def strongest_and_opportunity(record: dict) -> tuple:
    """
    Return (strongest_phrase, opportunity_phrase) for the results/email verdict.
    A pure display helper over the already-computed sub-scores — it performs no
    scoring of its own.
    """
    dims = [
        ("savings",      record["savings_score"]),
        ("resilience",   record["resilience_score"]),
        ("consistency",  record["consistency_score"]),
        ("commitment",   record["commitment_score"]),
        ("present_bias", record["present_bias_score"]),
    ]
    strongest = max(dims, key=lambda d: d[1])[0]
    weakest   = min(dims, key=lambda d: d[1])[0]
    return STRENGTH_PHRASES[strongest], OPPORTUNITY_PHRASES[weakest]

# ── ASSESSMENT STRUCTURE (data-driven; the UI renders this list) ──────────────
# kind: "single" (pick one), "multi2" (pick exactly two), "consent" (final gate).
# Demographic questions are flagged optional and used only in aggregate.

QUESTIONS = [
    {
        "id": "age_band", "kind": "single", "optional": True, "section": "About you",
        "prompt": "Which age group best describes you?",
        "subtitle": "Used only in aggregate, to compare life stages — never shown individually.",
        "options": [{"code": k, "label": v} for k, v in AGE_LABELS.items()],
    },
    {
        "id": "life_stage", "kind": "single", "optional": True, "section": "About you",
        "prompt": "Which best describes you?",
        "subtitle": "WealthMind studies financial behaviour across life stages, not just students.",
        "options": [{"code": k, "label": v} for k, v in LIFE_STAGE_LABELS.items()],
    },
    {
        "id": "gender", "kind": "single", "optional": True, "section": "About you",
        "prompt": "Gender (optional)",
        "subtitle": "Optional. Used only in aggregate research.",
        "options": [{"code": k, "label": v} for k, v in GENDER_LABELS.items()],
    },
    {
        "id": "currency", "kind": "single", "section": "Your finances",
        "prompt": "What currency do you usually receive income in?",
        "subtitle": "This only changes the income ranges shown next — everyone is "
                    "scored the same way.",
        "options": [{"code": k, "label": v} for k, v in CURRENCY_LABELS.items()],
    },
    {
        "id": "income", "kind": "single", "section": "Your finances", "concept": "Income",
        "prompt": "In a typical month, roughly how much money comes in?",
        "subtitle": "Allowance, part-time work, family support, business — your best estimate.",
        # NOTE: labels shown to the user are swapped per selected currency at render
        # time (see income_options); these default KES labels are the fallback.
        "options": [
            {"code": "i_u5",    "label": "Under KES 5,000"},
            {"code": "i_5_15",  "label": "KES 5,000–15,000"},
            {"code": "i_15_30", "label": "KES 15,000–30,000"},
            {"code": "i_30_60", "label": "KES 30,000–60,000"},
            {"code": "i_o60",   "label": "Above KES 60,000"},
        ],
    },
    {
        "id": "savings", "kind": "single", "section": "Your finances",
        "concept": "Permanent Income Hypothesis (Friedman, 1957)",
        "prompt": "Of the money that comes in, how much is usually left at month end?",
        "subtitle": "What is left after everything you spend.",
        "options": [
            {"code": "s_none",  "label": "Nothing — I often run short"},
            {"code": "s_tenth", "label": "A little — about 1 in 10"},
            {"code": "s_fifth", "label": "Some — about 1 in 5"},
            {"code": "s_third", "label": "A good amount — about a third"},
            {"code": "s_half",  "label": "Half or more"},
        ],
    },
    {
        "id": "commitment", "kind": "single", "section": "Your finances",
        "concept": "Capital accumulation (Solow)",
        "prompt": "Do you deliberately move money into savings or investment?",
        "subtitle": "M-Shwari, SACCO, M-Akiba, a bank account, shares — a deliberate transfer.",
        "options": [
            {"code": "c_never",  "label": "Never"},
            {"code": "c_occ",    "label": "Occasionally"},
            {"code": "c_little", "label": "Most months, a little"},
            {"code": "c_set",    "label": "Every month, a set amount"},
        ],
    },
    {
        "id": "buffer", "kind": "single", "section": "Your finances",
        "concept": "Buffer-stock saving theory (Deaton, 1991)",
        "prompt": "If your income stopped today, how long could savings cover your usual expenses?",
        "subtitle": "Your financial runway.",
        "options": [
            {"code": "b_week",  "label": "Less than a week"},
            {"code": "b_2week", "label": "About two weeks"},
            {"code": "b_1_2mo", "label": "One to two months"},
            {"code": "b_3_6mo", "label": "Three to six months"},
            {"code": "b_6plus", "label": "More than six months"},
        ],
    },
    {
        "id": "timing", "kind": "single", "section": "Your behaviour",
        "concept": "Hyperbolic discounting (Laibson, 1997)",
        "prompt": "When does most of your spending happen?",
        "subtitle": "Think about a typical month.",
        "options": [
            {"code": "t_after",  "label": "Mostly right after I get money"},
            {"code": "t_even",   "label": "Spread evenly through the month"},
            {"code": "t_end",    "label": "More toward the end"},
            {"code": "t_unsure", "label": "I'm not sure"},
        ],
    },
    {
        "id": "consistency", "kind": "single", "section": "Your behaviour",
        "concept": "Consumption smoothing (Hall, 1978)",
        "prompt": "How similar is your spending from one month to the next?",
        "subtitle": "Stable spending or unpredictable?",
        "options": [
            {"code": "v_very",   "label": "Very similar each month"},
            {"code": "v_rough",  "label": "Roughly similar"},
            {"code": "v_varies", "label": "It varies a lot"},
            {"code": "v_unpred", "label": "Totally unpredictable"},
        ],
    },
    {
        "id": "categories", "kind": "multi2", "section": "Your behaviour",
        "concept": "Consumption basket / Engel's Law",
        "prompt": "Where does most of your money go?",
        "subtitle": "Pick your top two.",
        "options": [{"code": k, "label": v} for k, v in CATEGORY_LABELS.items()],
    },
    {
        "id": "inflation", "kind": "single", "section": "Your behaviour",
        "concept": "Real vs nominal value (Fisher, 1930)",
        "prompt": "Compared with a year ago, your money buys…",
        "subtitle": "How your purchasing power feels.",
        "options": [
            {"code": "much_less",   "label": "Much less"},
            {"code": "little_less", "label": "A little less"},
            {"code": "same",        "label": "About the same"},
            {"code": "unsure",      "label": "Not sure"},
        ],
    },
]
# NOTE: the old in-flow consent question was removed. Research participation is
# now disclosed on the introduction and email screens, and every completed
# assessment is saved (score_assessment defaults consent="yes"). Email/contact
# data is captured upfront and stored SEPARATELY from the financial responses,
# linked only by an internal assessment id (see database.save_report_request).


# ── SCORING ───────────────────────────────────────────────────────────────────

def _present_bias_score(bias_index: float) -> float:
    """
    Convert the present-bias index to a 0–100 'time-consistency' score where
    higher = more time-consistent (less present-biased).
    index 1.0 → 100, 1.5 → 50, ≥2.0 → 0; reverse patterns (<1.0) clamp to 100.
    """
    return max(0.0, min(100.0, 100.0 - (bias_index - 1.0) * 100.0))


def score_assessment(answers: dict) -> dict:
    """
    Score a completed assessment and return the full record.

    `answers` keys: age_band, life_stage, gender (optional);
    income, savings, commitment, buffer, timing, consistency,
    categories (list of two codes), inflation; plus consent, currency,
    user_id (optional).

    Returns a dict containing the raw answer codes, the derived engine inputs,
    and the four headline scores — ready to hand to database.save_assessment()
    (which stores it only if consent == 'yes'). No transactions are created.
    """
    def _val(qid, band_map):
        code = answers.get(qid)
        if code in band_map:
            return code, band_map[code]
        dft_code, dft_val = _DEFAULTS.get(qid, (code, 0.0))
        return code, dft_val

    # ── Map answers → the tracker's intermediate quantities ───────────────────
    ans_income = answers.get("income")
    income_estimate = INCOME_BANDS.get(ans_income, 0.0)

    ans_savings,     savings_rate_pct      = _val("savings",     SAVINGS_RATE_BANDS)
    ans_commitment,  commitment_rate_pct   = _val("commitment",  COMMITMENT_BANDS)
    ans_buffer,      emergency_fund_months = _val("buffer",      BUFFER_MONTHS_BANDS)
    ans_timing,      bias_index            = _val("timing",      TIMING_BIAS_BANDS)
    ans_consistency, spending_cv           = _val("consistency", CONSISTENCY_CV_BANDS)

    categories = answers.get("categories") or []
    ans_categories = ",".join(categories[:2])
    ans_inflation = answers.get("inflation")

    # ── Apply the SHARED scoring functions (identical to the tracker) ─────────
    savings_score     = score_savings_rate(savings_rate_pct)
    commitment_score  = score_investment_commitment(commitment_rate_pct)
    resilience_score  = score_emergency_fund(emergency_fund_months)
    consistency_score = score_spending_consistency(spending_cv)

    health_score = (
        savings_score     * HEALTH_WEIGHTS["savings_rate"]   +
        resilience_score  * HEALTH_WEIGHTS["emergency_fund"] +
        consistency_score * HEALTH_WEIGHTS["consistency"]    +
        commitment_score  * HEALTH_WEIGHTS["commitment"]
    )

    present_bias_label, _ = classify_bias(bias_index)
    present_bias_score = _present_bias_score(bias_index)

    return {
        # provenance / demographics
        "user_id":     answers.get("user_id"),
        "source":      "assessment",
        "currency":    answers.get("currency", "KES"),
        "consent":     answers.get("consent", "yes"),
        "age_band":    answers.get("age_band"),
        "life_stage":  answers.get("life_stage"),
        "gender":      answers.get("gender"),
        # raw answer codes
        "ans_income":      ans_income,
        "ans_savings":     ans_savings,
        "ans_commitment":  ans_commitment,
        "ans_buffer":      ans_buffer,
        "ans_timing":      ans_timing,
        "ans_consistency": ans_consistency,
        "ans_categories":  ans_categories,
        "ans_inflation":   ans_inflation,
        # derived engine inputs
        "income_estimate":       income_estimate,
        "savings_rate_pct":      round(savings_rate_pct, 1),
        "commitment_rate_pct":   round(commitment_rate_pct, 1),
        "emergency_fund_months": round(emergency_fund_months, 2),
        "spending_cv":           round(spending_cv, 3),
        "bias_index":            round(bias_index, 2),
        # final scores
        "health_score":       round(health_score, 1),
        "savings_score":      round(savings_score, 1),
        "resilience_score":   round(resilience_score, 1),
        "consistency_score":  round(consistency_score, 1),
        "commitment_score":   round(commitment_score, 1),
        "present_bias_score": round(present_bias_score, 1),
        "present_bias_label": present_bias_label,
    }


# ── PERSONALISED INSIGHTS ─────────────────────────────────────────────────────

def generate_assessment_insights(record: dict) -> list[dict]:
    """
    Build the personalised economic narrative shown on the results page.

    Each insight follows the same four-part structure:
        suggests  — what your answers suggest
        concept   — which economic concept describes the behaviour
        long_term — what this means long term
        action    — one recommended action
    Returns a list ordered by salience. `tone` drives the card colour.
    """
    insights: list[dict] = []
    cur = record.get("currency", "KES")

    # ── Present bias (Laibson) ────────────────────────────────────────────────
    idx = record["bias_index"]
    label = record["present_bias_label"]
    if idx >= 1.6:
        insights.append({
            "title": "Spending front-loads sharply after payday",
            "tone": "critical",
            "concept": "Hyperbolic discounting (Laibson, 1997)",
            "suggests": (
                f"You appear strongly present-biased — spending is concentrated "
                f"shortly after income arrives (index {idx:.2f})."
            ),
            "long_term": (
                "Money spent early in the cycle compounds into a large foregone "
                "balance over years — the most common and costly departure from "
                "time-consistent preferences."
            ),
            "action": "Automate a transfer to savings on the day income arrives, "
                      "before discretionary spending begins — a commitment device.",
        })
    elif idx >= 1.1:
        insights.append({
            "title": "A moderate pull toward early-month spending",
            "tone": "caution",
            "concept": "Hyperbolic discounting (Laibson, 1997)",
            "suggests": (
                f"You appear moderately present-biased. Spending is concentrated "
                f"shortly after income arrives, consistent with Laibson's model "
                f"of hyperbolic discounting (index {idx:.2f})."
            ),
            "long_term": "Mild but persistent — small early-month excesses accumulate "
                         "across a year.",
            "action": "Try setting aside savings in the first 48 hours after income arrives.",
        })
    else:
        insights.append({
            "title": "Time-consistent spending",
            "tone": "positive",
            "concept": "Consumption smoothing (Hall, 1978)",
            "suggests": (
                f"Your spending is well distributed across the month "
                f"({label.lower()}, index {idx:.2f})."
            ),
            "long_term": "Smoothed consumption is exactly what rational, time-consistent "
                         "models predict — a genuine behavioural strength.",
            "action": "Maintain it; redirect the stability into a regular investment habit.",
        })

    # ── Resilience (Deaton buffer stock) ──────────────────────────────────────
    months = record["emergency_fund_months"]
    if months < 1:
        insights.append({
            "title": f"About {months:.1f} months of financial resilience",
            "tone": "critical",
            "concept": "Buffer-stock saving theory (Deaton, 1991)",
            "suggests": f"Your savings would cover roughly {months:.1f} months without income.",
            "long_term": "Deaton's buffer-stock model suggests households maintain "
                         "precautionary savings to reduce vulnerability; below one month, "
                         "a single shock forces costly borrowing.",
            "action": "Aim first for a one-month buffer, then build toward three.",
        })
    elif months < 3:
        insights.append({
            "title": f"About {months:.1f} months of financial resilience",
            "tone": "caution",
            "concept": "Buffer-stock saving theory (Deaton, 1991)",
            "suggests": f"You have approximately {months:.1f} month(s) of financial resilience. "
                        f"Deaton's buffer-stock model suggests households maintain precautionary "
                        f"savings to reduce vulnerability.",
            "long_term": "You are below the 3–6 month buffer regulators treat as the "
                         "standard shock absorber.",
            "action": "Build steadily toward three months of expenses in liquid savings.",
        })
    else:
        insights.append({
            "title": f"A solid {months:.1f}-month buffer",
            "tone": "positive",
            "concept": "Buffer-stock saving theory (Deaton, 1991)",
            "suggests": f"Your savings would cover about {months:.1f} months without income.",
            "long_term": "You sit within or above the recommended 3–6 month buffer — strong "
                         "protection against income shocks.",
            "action": "Once past six months, direct surplus toward higher-return investment.",
        })

    # ── Savings behaviour (Friedman) ──────────────────────────────────────────
    rate = record["savings_rate_pct"]
    if rate < 10:
        insights.append({
            "title": "Savings rate below the wealth-building benchmark",
            "tone": "caution",
            "concept": "Permanent Income Hypothesis (Friedman, 1957)",
            "suggests": f"You keep roughly {rate:.0f}% of income — below the 20% benchmark.",
            "long_term": "Friedman's theory ties long-run wealth to the fraction of permanent "
                         "income saved; a low rate caps accumulation regardless of income.",
            "action": "Target a 1-percentage-point increase in your savings rate each term.",
        })
    elif rate < 20:
        insights.append({
            "title": "A developing savings habit",
            "tone": "info",
            "concept": "Permanent Income Hypothesis (Friedman, 1957)",
            "suggests": f"You keep about {rate:.0f}% of income — approaching the 20% benchmark.",
            "long_term": "Consistency at this level compounds meaningfully over decades.",
            "action": "Push toward 20% — the rate most associated with long-run wealth building.",
        })
    else:
        insights.append({
            "title": "A strong savings rate",
            "tone": "positive",
            "concept": "Permanent Income Hypothesis (Friedman, 1957)",
            "suggests": f"You keep about {rate:.0f}% of income — at or above the 20% benchmark.",
            "long_term": "A high, stable savings rate is the single strongest predictor of "
                         "long-run wealth accumulation.",
            "action": "Ensure savings are invested, not idle, so returns compound.",
        })

    # ── Inflation / real value (Fisher) — insight only, not scored ────────────
    infl = record.get("ans_inflation")
    if infl in ("much_less", "little_less"):
        insights.append({
            "title": "You're feeling the gap between nominal and real value",
            "tone": "info",
            "concept": "Real vs nominal value (Fisher, 1930)",
            "suggests": "You sense your money buys less than a year ago — that is inflation "
                        "eroding real purchasing power even when nominal balances are unchanged.",
            "long_term": "At Kenya's recent inflation, cash held idle loses several percent of "
                         "real value each year; the Fisher relation makes this precise.",
            "action": "Hold savings in interest-bearing or return-generating form to offset "
                      "inflation, rather than as idle cash.",
        })

    return insights
