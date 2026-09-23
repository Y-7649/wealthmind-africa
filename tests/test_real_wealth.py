"""
tests/test_real_wealth.py
WealthMind Africa — Real vs Nominal Wealth engine tests (Version 1.1)

Verifies the maths behind the flagship Version 1.1 feature:

  1. FISHER, NOT SUBTRACTION — the real return divides (1+g) by (1+i); it is not
     g − i.
  2. WORKED EXAMPLE — KES 100,000 at 10% for 5 years against 6% inflation gives
     the expected nominal and real figures.
  3. ROBUSTNESS — zero/negative/degenerate inputs never crash and behave sanely.

This engine is NOT part of the Version 1.0 assessment scoring, so these tests are
entirely independent of the assessment regression suite.

Runs standalone (`python tests/test_real_wealth.py`) printing a report, and is
also importable by pytest (functions named test_*).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.real_wealth import project_real_wealth, real_growth_annual


def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ── 1. FISHER, NOT SUBTRACTION ────────────────────────────────────────────────

def test_fisher_not_subtraction():
    """Real annual return divides rather than subtracts."""
    r = real_growth_annual(0.10, 0.06)
    assert _close(r, (1.10 / 1.06) - 1.0)          # exact Fisher
    assert _close(r, 0.0377358490566, tol=1e-9)    # ≈ 3.77%
    assert abs(r - 0.04) > 0.002                    # emphatically NOT 10% − 6%


def test_zero_inflation_real_equals_nominal():
    """With no inflation, real return equals nominal return."""
    res = project_real_wealth(100000, 0.10, 0.0, 5)
    assert _close(res.real_return_total, res.nominal_return_total)
    assert _close(res.real_value, res.nominal_value)


# ── 2. WORKED EXAMPLE ─────────────────────────────────────────────────────────

def test_worked_example_100k():
    """KES 100,000 · 10% · 5 years · 6% inflation."""
    res = project_real_wealth(100000, 0.10, 0.06, 5)
    assert _close(res.nominal_value, 161051.00, tol=0.01)
    assert _close(res.real_value, 120346.68, tol=0.5)
    assert _close(res.nominal_return_total, 0.61051, tol=1e-4)
    assert _close(res.real_return_total, 0.2034668, tol=1e-4)
    # purchasing-power change is the real return of the invested sum
    assert _close(res.purchasing_power_change, res.real_return_total)
    # holding it as idle cash instead loses purchasing power
    assert _close(res.cash_purchasing_power_change, (1.0 / 1.06 ** 5) - 1.0, tol=1e-9)
    assert res.cash_purchasing_power_change < 0


def test_bigger_number_smaller_real():
    """When growth trails inflation, the number grows but real value shrinks."""
    res = project_real_wealth(100000, 0.03, 0.08, 10)
    assert res.nominal_value > res.start          # bigger number
    assert res.real_value < res.start             # worth less
    assert res.real_return_total < 0              # genuinely worse off


# ── 3. ROBUSTNESS ─────────────────────────────────────────────────────────────

def test_zero_horizon():
    res = project_real_wealth(100000, 0.10, 0.06, 0)
    assert _close(res.nominal_value, 100000)
    assert _close(res.real_value, 100000)
    assert _close(res.nominal_return_total, 0.0)
    assert _close(res.real_return_total, 0.0)
    assert len(res.series) == 1


def test_zero_start():
    res = project_real_wealth(0, 0.10, 0.06, 5)
    assert _close(res.nominal_value, 0.0)
    assert _close(res.real_value, 0.0)


def test_growth_equals_inflation():
    """Growing exactly with inflation means no real gain."""
    res = project_real_wealth(50000, 0.05, 0.05, 10)
    assert _close(res.real_return_total, 0.0, tol=1e-9)
    assert _close(res.real_value, res.start, tol=1e-6)


def test_negative_inputs_do_not_crash():
    """Nonsensical inputs are clamped, not fatal."""
    res = project_real_wealth(-100, -0.5, -2.0, 3)   # negative everything
    assert res.start == 0.0                          # clamped to 0
    assert isinstance(res.real_value, float)


def test_series_shape():
    res = project_real_wealth(100000, 0.08, 0.05, 7)
    assert len(res.series) == 8                       # years + 1 (0..7)
    assert _close(res.series[0]["nominal"], 100000)
    assert _close(res.series[0]["real"], 100000)
    assert _close(res.series[-1]["nominal"], res.nominal_value)
    assert _close(res.series[-1]["real"], res.real_value)


# ── STANDALONE RUNNER ─────────────────────────────────────────────────────────

def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}  — {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {t.__name__}  — {type(e).__name__}: {e}")
    print(f"\nReal vs Nominal Wealth: {passed}/{len(tests)} tests passed.")
    return passed == len(tests)


if __name__ == "__main__":
    ok = _run()
    sys.exit(0 if ok else 1)
