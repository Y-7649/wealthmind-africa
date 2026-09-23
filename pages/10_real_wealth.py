"""
pages/10_real_wealth.py
WealthMind Africa — Real vs Nominal Wealth  (Version 1.1 flagship, public)

The central question:
    "Did your money actually become more valuable,
     or did it just become a bigger number?"

A public, no-login educational simulator. The participant enters a starting
amount, an expected annual growth rate, and a time horizon, then chooses an
inflation assumption (with real Kenyan CPI shown for context). The tool shows,
side by side, the future NOMINAL value and the INFLATION-ADJUSTED value, plus
the nominal return, real return, and purchasing-power change.

All maths lives in the pure, unit-tested core.real_wealth engine. This page is
UI only and introduces NO new WealthMind score — it never touches the Version
1.0 assessment engine.

Educational simulation. Not investment advice.

Created by Yash Karia
"""

import streamlit as st
import plotly.graph_objects as go

from core.real_wealth import project_real_wealth, plain_verdict, real_growth_annual
from data.kenya_macro import get_inflation_history
from data.nse_index import data_status
from utils.sidebar import render_sidebar
from utils.footer import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Real vs Nominal Wealth — WealthMind Africa",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar("real_wealth")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── PAGE-SCOPED STYLES ────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .rw-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin:0.4rem 0 0.2rem; }
    .rw-tile { background:linear-gradient(145deg,#141B28,#111620); border:1px solid #1E2738;
               border-radius:12px; padding:1rem 1.15rem; }
    .rw-tile .lbl { font-size:0.66rem; font-weight:700; color:#4A6070; text-transform:uppercase;
                    letter-spacing:0.09em; margin-bottom:0.35rem; }
    .rw-tile .val { font-size:1.6rem; font-weight:800; letter-spacing:-0.02em; line-height:1.05; }
    .rw-tile .sub { font-size:0.72rem; color:#8899AA; margin-top:0.2rem; }
    .rw-hero { display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin:0.6rem 0 0.3rem; }
    .rw-big  { border-radius:14px; padding:1.3rem 1.4rem; border:1px solid #1E2738; }
    .rw-big .cap { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; }
    .rw-big .amt { font-size:2.15rem; font-weight:800; letter-spacing:-0.03em; line-height:1.1; margin-top:0.25rem; }
    .rw-big .note{ font-size:0.75rem; color:#8899AA; margin-top:0.3rem; line-height:1.45; }
    @media (max-width:640px){
        .rw-grid { grid-template-columns:repeat(2,1fr); }
        .rw-hero { grid-template-columns:1fr; }
        .rw-big .amt { font-size:1.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div style="padding:0.4rem 0 0.2rem;">
        <span style="font-size:0.68rem;font-weight:700;color:#00C49F;text-transform:uppercase;
              letter-spacing:0.16em;">Understand · Simulate &nbsp;·&nbsp; Version 1.1</span>
        <h1 style="font-size:2rem;color:#E2E8F0;letter-spacing:-0.03em;line-height:1.2;
                   margin:0.5rem 0 0.4rem;">Real vs Nominal Wealth</h1>
        <p style="color:#8899AA;font-size:1rem;line-height:1.6;max-width:640px;margin:0;">
            Did your money actually become more valuable, or did it just become a
            <em style="color:#CCDDE8;">bigger number</em>? Earning 10% while inflation
            runs 6% does <strong style="color:#CCDDE8;">not</strong> mean your purchasing
            power rose 10%. This tool shows the difference.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── CURRENCY ──────────────────────────────────────────────────────────────────

_CUR = {"KES": "KES", "USD": "USD", "GBP": "GBP", "EUR": "EUR", "INR": "INR"}
cur_c1, _cur_sp = st.columns([1, 3])
with cur_c1:
    currency = st.selectbox("Currency", list(_CUR.keys()), index=0,
                            help="Only changes the display label — the maths is identical.")

st.divider()

# ── INPUTS ────────────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
with c1:
    start = st.number_input(f"Starting amount ({currency})", min_value=0.0,
                            value=100000.0, step=10000.0, format="%.0f")
with c2:
    years = st.slider("Time horizon (years)", min_value=1, max_value=40, value=5)
with c3:
    growth_pct = st.slider("Expected annual growth %", min_value=0.0, max_value=30.0,
                           value=10.0, step=0.5)
with c4:
    inflation_pct = st.slider("Assumed inflation % (your scenario)", min_value=0.0,
                              max_value=20.0, value=5.0, step=0.5)

# Kenyan CPI context — clearly labelled OFFICIAL observations vs the user's
# assumption above. Distinguishing the two is a deliberate honesty requirement.
_hist = get_inflation_history()
_recent = _hist[-5:]
_ctx = " · ".join(
    f"{h['year']} {h['rate']:.1f}%" + ("*" if h["year"] >= 2025 else "")
    for h in _recent
)
st.markdown(
    f"<div style='background:#0F1824;border:1px solid #1E2738;border-radius:10px;"
    f"padding:0.7rem 1rem;margin:0.2rem 0 0.2rem;'>"
    f"<span style='font-size:0.66rem;font-weight:700;color:#4A6070;text-transform:uppercase;"
    f"letter-spacing:0.09em;'>Kenya headline inflation — official observations</span><br>"
    f"<span style='color:#AEBECD;font-size:0.85rem;'>{_ctx}</span><br>"
    f"<span style='font-size:0.72rem;color:#8899AA;'>Source: Kenya National Bureau of "
    f"Statistics (KNBS), CPI reports. *2025 provisional/estimate. The slider above is "
    f"<strong style='color:#AEBECD;'>your own assumption</strong>, not an official figure.</span></div>",
    unsafe_allow_html=True,
)

# ── COMPUTE (pure engine) ─────────────────────────────────────────────────────

g = growth_pct / 100.0
i = inflation_pct / 100.0
res = project_real_wealth(start, g, i, years)

def _money(v):  # compact currency formatter
    return f"{currency} {v:,.0f}"

def _pct(v):
    return f"{v * 100:+.1f}%"

real_col = "#00C49F" if res.real_return_total >= 0 else "#FF4444"
inflation_tax = res.nominal_value - res.real_value

# ── VERDICT ───────────────────────────────────────────────────────────────────

st.markdown(
    f"<div style='background:#141B28;border:1px solid #1E2738;border-left:3px solid #00C49F;"
    f"border-radius:0 12px 12px 0;padding:1rem 1.25rem;margin:0.6rem 0 0.4rem;'>"
    f"<div style='color:#E2E8F0;font-size:1rem;line-height:1.6;'>{plain_verdict(res, currency)}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── HERO CONTRAST: nominal vs inflation-adjusted ──────────────────────────────

st.markdown(
    f"""
    <div class="rw-hero">
      <div class="rw-big" style="background:linear-gradient(160deg,#0F1E1A,#0C1616);
           border-color:rgba(0,196,159,0.3);">
        <div class="cap" style="color:#00C49F;">Future Nominal Value</div>
        <div class="amt" style="color:#00C49F;">{_money(res.nominal_value)}</div>
        <div class="note">What the account balance will <em>show</em> in {res.years} years —
             {_money(res.start)} growing at {growth_pct:.1f}% a year.</div>
      </div>
      <div class="rw-big" style="background:linear-gradient(160deg,#1E1710,#161009);
           border-color:rgba(255,136,0,0.3);">
        <div class="cap" style="color:#FF8800;">Inflation-Adjusted Value</div>
        <div class="amt" style="color:#FF8800;">{_money(res.real_value)}</div>
        <div class="note">What that future amount is <em>really worth</em> in today's
             purchasing power, after {inflation_pct:.1f}% annual inflation.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"<div style='text-align:center;color:#9AA6B2;font-size:0.85rem;margin:0.1rem 0 0.5rem;'>"
    f"Inflation quietly removes about <strong style='color:#FF8800;'>{_money(inflation_tax)}</strong> "
    f"of purchasing power over {res.years} years — value that never shows up on the balance.</div>",
    unsafe_allow_html=True,
)

# ── DETAIL TILES: the six figures ─────────────────────────────────────────────

st.markdown(
    f"""
    <div class="rw-grid">
      <div class="rw-tile"><div class="lbl">Starting Wealth</div>
        <div class="val" style="color:#E2E8F0;">{_money(res.start)}</div>
        <div class="sub">today</div></div>
      <div class="rw-tile"><div class="lbl">Nominal Return</div>
        <div class="val" style="color:#00C49F;">{_pct(res.nominal_return_total)}</div>
        <div class="sub">total over {res.years} yrs · {growth_pct:.1f}%/yr</div></div>
      <div class="rw-tile"><div class="lbl">Real Return</div>
        <div class="val" style="color:{real_col};">{_pct(res.real_return_total)}</div>
        <div class="sub">total, after inflation</div></div>
      <div class="rw-tile"><div class="lbl">Purchasing Power Change</div>
        <div class="val" style="color:{real_col};">{_pct(res.purchasing_power_change)}</div>
        <div class="sub">what your money can actually buy</div></div>
      <div class="rw-tile"><div class="lbl">Real Return / year</div>
        <div class="val" style="color:{real_col};">{_pct(res.real_return_annual)}</div>
        <div class="sub">Fisher: (1+g)/(1+i) − 1</div></div>
      <div class="rw-tile"><div class="lbl">If Held As Idle Cash</div>
        <div class="val" style="color:#FF4444;">{_pct(res.cash_purchasing_power_change)}</div>
        <div class="sub">purchasing power lost doing nothing</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── CHART: nominal vs real over time ──────────────────────────────────────────

xs = [p["year"] for p in res.series]
nominal_ys = [p["nominal"] for p in res.series]
real_ys = [p["real"] for p in res.series]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=xs, y=nominal_ys, name="Nominal value", mode="lines",
    line=dict(color="#00C49F", width=3),
    hovertemplate=f"Year %{{x}}<br>{currency} %{{y:,.0f}} (nominal)<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=xs, y=real_ys, name="Real value (today's money)", mode="lines",
    line=dict(color="#FF8800", width=3, dash="dot"),
    fill="tonexty", fillcolor="rgba(255,136,0,0.06)",
    hovertemplate=f"Year %{{x}}<br>{currency} %{{y:,.0f}} (real)<extra></extra>",
))
fig.update_layout(
    height=340, margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8899AA", family="Inter"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    xaxis=dict(title="Years", gridcolor="#1A2030", zeroline=False),
    yaxis=dict(title=f"{currency}", gridcolor="#1A2030", zeroline=False),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.caption(
    "The gap between the two lines is inflation's bite: the same money, worth less "
    "each year in what it can actually buy."
)

st.divider()

# ── INVESTMENT vs INFLATION (Fisher explainer) ────────────────────────────────

real_annual = real_growth_annual(g, i)
st.markdown(
    f"""
    <div style="background:linear-gradient(145deg,#141B28,#111620);border:1px solid #1E2738;
         border-radius:14px;padding:1.2rem 1.35rem;margin:0.3rem 0;">
      <div style="font-size:0.7rem;font-weight:700;color:#00C49F;text-transform:uppercase;
           letter-spacing:0.1em;margin-bottom:0.6rem;">Investment vs Inflation</div>
      <div style="display:flex;flex-wrap:wrap;gap:1.4rem;align-items:baseline;margin-bottom:0.7rem;">
        <div><span style="color:#8899AA;font-size:0.78rem;">Your investment grew</span><br>
             <span style="color:#00C49F;font-size:1.3rem;font-weight:800;">{growth_pct:+.1f}%</span></div>
        <div><span style="color:#8899AA;font-size:0.78rem;">Prices rose</span><br>
             <span style="color:#FF8800;font-size:1.3rem;font-weight:800;">{inflation_pct:+.1f}%</span></div>
        <div><span style="color:#8899AA;font-size:0.78rem;">Real purchasing-power growth</span><br>
             <span style="color:{real_col};font-size:1.3rem;font-weight:800;">≈ {real_annual * 100:+.1f}%</span></div>
      </div>
      <div style="color:#9AA6B2;font-size:0.85rem;line-height:1.6;">
        Not simply {growth_pct:.0f}% − {inflation_pct:.0f}% = {growth_pct - inflation_pct:.0f}%.
        Inflation applies to the <em>grown</em> amount, not just the original, so the exact
        real return divides rather than subtracts: (1 + {growth_pct/100:.2f}) ÷
        (1 + {inflation_pct/100:.2f}) − 1 ≈ {real_annual * 100:.1f}%.
      </div>
    </div>
    <div style="text-align:center;color:#4A6070;font-size:0.75rem;margin:0.5rem 0 0.2rem;">
        📘 Educational simulation. Not investment advice.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── NSE — honest, understated foundation note ─────────────────────────────────
# No fabricated market data. A single quiet line only (see data/nse_index.py).
_nse = data_status()
if not _nse["available"]:
    st.caption(f"🇰🇪 {_nse['message']} For now, choose your own growth assumption above.")

render_footer()
