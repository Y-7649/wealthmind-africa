"""
data/nse_index.py
WealthMind Africa — Nairobi Securities Exchange (NSE) data interface

STATUS: interface only. NO market data is bundled, because as of this release
there is no free, reliable, legally reproducible NSE historical-price API.
(The NSE licenses market data commercially; the only free primary sources —
CBK and KNBS statistical bulletins — are PDFs, not an API.) Rather than scrape
fragile third-party sites or fabricate an index series, Version 1.1 ships this
clean interface so a legitimate NSE dataset can be plugged in later WITHOUT
rewriting the Real vs Nominal Wealth simulation.

────────────────────────────────────────────────────────────────────────────
HOW TO ADD REAL DATA LATER
────────────────────────────────────────────────────────────────────────────
Populate `_NSE_SERIES` (or load it from a bundled CSV / a licensed API) with a
list of observations, each a dict with these fields:

    date        str   ISO-8601 calendar date, "YYYY-MM-DD"
                      (month-end or period-end is fine; be consistent)
    index_id    str   the index or asset identifier, e.g. "NSE20" (NSE 20 Share
                      Index) or "NASI" (NSE All-Share Index)
    value       float the index level / closing price on that date (points)
    dividend    float OPTIONAL — dividend or income component for that period,
                      in the same units; omit or None if not available
    source      str   provenance, e.g. "CBK Statistical Bulletin, Table X (2026)"

Also set `NSE_DATA_AVAILABLE = True` and record `NSE_DATA_SOURCE` /
`NSE_DATA_AS_OF`. The accessor functions below already return this shape, so the
UI needs no changes — it checks `nse_data_available()` and, when true, calls
`get_nse_series()` / `get_annual_returns()`.

Do NOT populate this with estimated, interpolated, or scraped values presented
as observations. Accuracy and honest provenance matter more than appearing
"live".
"""

from typing import Optional

# ── AVAILABILITY FLAGS ────────────────────────────────────────────────────────
# Flip to True only once a legitimate, reproducible dataset is bundled above.
NSE_DATA_AVAILABLE = False
NSE_DATA_SOURCE: Optional[str] = None   # e.g. "CBK Statistical Bulletin (2026)"
NSE_DATA_AS_OF: Optional[str] = None    # e.g. "2026-06-30"

# The expected schema of each observation (documentation + light validation).
NSE_SERIES_SCHEMA = {
    "date":     "str  ISO-8601 'YYYY-MM-DD'",
    "index_id": "str  index/asset id, e.g. 'NSE20' or 'NASI'",
    "value":    "float index level / closing price (points)",
    "dividend": "float OPTIONAL income/dividend component (same units)",
    "source":   "str  provenance / citation",
}

# Intentionally empty. See module docstring for how to populate legitimately.
_NSE_SERIES: list[dict] = []


# ── ACCESSORS ─────────────────────────────────────────────────────────────────

def nse_data_available() -> bool:
    """True only when a legitimate NSE dataset has been bundled."""
    return bool(NSE_DATA_AVAILABLE and _NSE_SERIES)


def data_status() -> dict:
    """
    Machine-readable status for the UI. When data is unavailable the UI should
    NOT pretend an NSE simulation exists — it may show a single, understated
    'coming in a future data release' line, nothing more.
    """
    return {
        "available": nse_data_available(),
        "source":    NSE_DATA_SOURCE,
        "as_of":     NSE_DATA_AS_OF,
        "message": (
            "Kenyan market (NSE) comparison coming in a future data release."
            if not nse_data_available()
            else f"NSE data: {NSE_DATA_SOURCE} (as of {NSE_DATA_AS_OF})."
        ),
    }


def get_nse_series(index_id: str = "NSE20") -> list[dict]:
    """
    Return the observations for a given index id (empty until data is bundled).
    Each item follows NSE_SERIES_SCHEMA.
    """
    if not nse_data_available():
        return []
    return [row for row in _NSE_SERIES if row.get("index_id") == index_id]


def get_annual_returns(index_id: str = "NSE20") -> list[dict]:
    """
    Convenience view for the investment simulation: year-on-year price return
    derived from the bundled series. Returns [] until legitimate data exists,
    so callers can safely check `nse_data_available()` first.

    Shape: [{"year": int, "return": float}]  (return as a decimal, price-only)
    """
    series = get_nse_series(index_id)
    if len(series) < 2:
        return []

    by_year = {}
    for row in sorted(series, key=lambda r: r["date"]):
        by_year[row["date"][:4]] = row["value"]   # keep the latest value per year

    years = sorted(by_year.keys())
    out = []
    for prev, cur in zip(years, years[1:]):
        if by_year[prev]:
            out.append({
                "year": int(cur),
                "return": (by_year[cur] - by_year[prev]) / by_year[prev],
            })
    return out
