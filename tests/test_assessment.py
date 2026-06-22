"""
tests/test_assessment.py
WealthMind Africa — Assessment scoring tests

Verifies the three properties the assessment must hold:

  1. ONE SOURCE OF TRUTH — the assessment scores a respondent using the *exact*
     same function objects and weights as the long-term tracker (identity checks,
     not just equal values).
  2. CORRECT MAPPING — worked examples produce the expected scores on the shared
     curves.
  3. ROBUSTNESS — every answer option maps to a band, present-bias scoring is
     correct at the edges, and consent never affects the computed scores.

Runs standalone (`python tests/test_assessment.py`) printing a report, and is
also importable by pytest (functions named test_*).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.assessment as A
import core.health_score as H
import core.present_bias as P

_TOL = 0.05


def _close(a, b, tol=_TOL):
    return abs(a - b) <= tol


# ── 1. ONE SOURCE OF TRUTH ────────────────────────────────────────────────────

def test_single_source_of_truth():
    """The assessment must reuse the tracker's exact scoring objects."""
    assert A.score_savings_rate          is H.score_savings_rate          is H._score_savings_rate
    assert A.score_emergency_fund        is H.score_emergency_fund        is H._score_emergency_fund
    assert A.score_spending_consistency  is H.score_spending_consistency  is H._score_spending_consistency
    assert A.score_investment_commitment is H.score_investment_commitment is H._score_investment_commitment
    assert A.classify_bias               is P.classify_bias               is P._classify_bias
    assert A.HEALTH_WEIGHTS              is H.HEALTH_WEIGHTS


def test_health_composite_matches_tracker_formula():
    """Assessment health score == the tracker's weighted composite, recomputed independently."""
    answers = _disciplined_answers()
    rec = A.score_assessment(answers)
    w = H.HEALTH_WEIGHTS
    expected = (
        rec["savings_score"]     * w["savings_rate"]   +
        rec["resilience_score"]  * w["emergency_fund"] +
        rec["consistency_score"] * w["consistency"]    +
        rec["commitment_score"]  * w["commitment"]
    )
    assert _close(rec["health_score"], round(expected, 1))


# ── 2. WORKED EXAMPLES ────────────────────────────────────────────────────────

def _stretched_answers():
    return {
        "income": "i_5_15", "savings": "s_tenth", "commitment": "c_occ",
        "buffer": "b_2week", "timing": "t_after", "consistency": "v_varies",
        "categories": ["food", "transport"], "inflation": "little_less",
        "age_band": "18_24", "life_stage": "university", "consent": "yes",
    }


def _disciplined_answers():
    return {
        "income": "i_15_30", "savings": "s_third", "commitment": "c_set",
        "buffer": "b_3_6mo", "timing": "t_even", "consistency": "v_very",
        "categories": ["rent", "food"], "inflation": "same",
        "age_band": "25_34", "life_stage": "working", "consent": "yes",
    }


def test_worked_example_stretched():
    rec = A.score_assessment(_stretched_answers())
    assert _close(rec["savings_score"],      35.0)   # score_savings_rate(10)
    assert _close(rec["resilience_score"],   12.5)   # score_emergency_fund(0.5)
    assert _close(rec["consistency_score"],  38.0)   # score_spending_consistency(0.38)
    assert _close(rec["commitment_score"],   20.0)   # score_investment_commitment(2)
    assert _close(rec["health_score"],       26.6)
    assert _close(rec["present_bias_score"], 20.0)   # index 1.8
    assert rec["present_bias_label"] == "Strong Present Bias"


def test_worked_example_disciplined():
    rec = A.score_assessment(_disciplined_answers())
    assert _close(rec["savings_score"],      100.0)  # score_savings_rate(33)
    assert _close(rec["resilience_score"],    75.0)  # score_emergency_fund(4.5)
    assert _close(rec["consistency_score"],   86.0)  # score_spending_consistency(0.07)
    assert _close(rec["commitment_score"],    88.0)  # score_investment_commitment(12)
    assert _close(rec["health_score"],        87.9)
    assert _close(rec["present_bias_score"], 100.0)  # index 1.0
    assert rec["present_bias_label"] == "No Detectable Bias"


# ── 3. ROBUSTNESS ─────────────────────────────────────────────────────────────

def test_present_bias_score_edges():
    assert _close(A._present_bias_score(1.0), 100.0)
    assert _close(A._present_bias_score(1.5),  50.0)
    assert _close(A._present_bias_score(1.8),  20.0)
    assert _close(A._present_bias_score(2.0),   0.0)
    assert _close(A._present_bias_score(0.8), 100.0)   # reverse pattern clamps to 100


def test_every_option_maps_to_a_band():
    """No scored answer option can be missing from its band map."""
    band_for = {
        "savings": A.SAVINGS_RATE_BANDS,
        "commitment": A.COMMITMENT_BANDS,
        "buffer": A.BUFFER_MONTHS_BANDS,
        "timing": A.TIMING_BIAS_BANDS,
        "consistency": A.CONSISTENCY_CV_BANDS,
        "income": A.INCOME_BANDS,
    }
    for q in A.QUESTIONS:
        if q["id"] in band_for:
            for opt in q["options"]:
                assert opt["code"] in band_for[q["id"]], f"{q['id']}:{opt['code']} unmapped"


def test_consent_does_not_affect_scores():
    yes = A.score_assessment({**_stretched_answers(), "consent": "yes"})
    no  = A.score_assessment({**_stretched_answers(), "consent": "no"})
    for k in ("health_score", "present_bias_score", "resilience_score", "savings_score"):
        assert yes[k] == no[k]
    assert no["consent"] == "no"


def test_insights_structure():
    rec = A.score_assessment(_stretched_answers())
    insights = A.generate_assessment_insights(rec)
    assert len(insights) >= 3
    for ins in insights:
        for key in ("title", "concept", "suggests", "long_term", "action", "tone"):
            assert key in ins and ins[key]


# ── STANDALONE RUNNER ─────────────────────────────────────────────────────────

def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    print("\n" + "=" * 70)
    print("  WealthMind — Assessment Scoring Tests")
    print("=" * 70)
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")

    print("-" * 70)
    print(f"  {passed}/{len(tests)} passed")

    # Worked-example table (proof the mapping yields a realistic spread)
    print("\n  Worked examples (scored on the SAME curves as the tracker):")
    print("  " + "-" * 66)
    for name, ans in [("Stretched student", _stretched_answers()),
                      ("Disciplined saver", _disciplined_answers())]:
        r = A.score_assessment(ans)
        print(f"  {name:<18}  Health {r['health_score']:>5}/100   "
              f"Savings {r['savings_score']:>5}   "
              f"Resilience {r['resilience_score']:>5}   "
              f"PresentBias {r['present_bias_score']:>5} ({r['present_bias_label']})")
    print("  " + "-" * 66)

    print("\n  Single-source-of-truth identity check:")
    print(f"    assessment.score_savings_rate IS health._score_savings_rate  -> "
          f"{A.score_savings_rate is H._score_savings_rate}")
    print(f"    assessment.classify_bias       IS present_bias._classify_bias -> "
          f"{A.classify_bias is P._classify_bias}")
    print(f"    assessment.HEALTH_WEIGHTS      IS health.HEALTH_WEIGHTS       -> "
          f"{A.HEALTH_WEIGHTS is H.HEALTH_WEIGHTS}")
    print("=" * 70 + "\n")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run())
