"""
pages/0_kenya_context.py
WealthMind Africa — Kenya Economic Context

PUBLIC flagship page. No login required.
Accessible directly from the landing page.

A premium financial terminal-style dashboard presenting Kenya's macroeconomic
environment — inflation, growth, monetary policy, financial inclusion, and
mobile money — with Kenya vs Sub-Saharan Africa comparisons.

Design inspiration: Financial Times · Bloomberg · World Bank data explorer.

Created by Yash Karia
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

from utils.styles import inject_global_styles
from utils.footer import render_footer
from data.kenya_macro import (
    get_macro_snapshot,
    get_ssa_comparison,
    get_gdp_history,
    get_inflation_history,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Kenya Economic Context — WealthMind Africa",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_styles()

# ── TICKER + EXTRA CSS ────────────────────────────────────────────────────────
# Pure-CSS scrolling data ticker (no JavaScript required).
# Content is duplicated so the loop is seamless.

st.markdown(
    """
    <style>
    @keyframes ticker-scroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .kec-ticker-wrapper {
        overflow: hidden;
        background: #080D18;
        border-top: 1px solid rgba(0,196,159,0.18);
        border-bottom: 1px solid rgba(0,196,159,0.18);
        padding: 0.55rem 0;
        width: 100%;
        margin-bottom: 0;
    }
    .kec-ticker-inner {
        display: inline-block;
        white-space: nowrap;
        animation: ticker-scroll 40s linear infinite;
    }
    .kec-ticker-item {
        display: inline-block;
        font-family: 'Inter', monospace;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        padding: 0 2.2rem;
        color: #7A9AB0;
    }
    .kec-ticker-item .kec-val { color: #00C49F; font-weight: 700; }
    .kec-ticker-item .kec-neg { color: #FF8800; font-weight: 700; }
    .kec-ticker-sep {
        display: inline-block;
        color: rgba(0,196,159,0.25);
        padding: 0 0.5rem;
        font-size: 0.65rem;
    }

    /* Hero counter blocks */
    .kec-hero-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.6rem 0;
    }
    .kec-hero-card {
        background: linear-gradient(145deg, #0F1824 0%, #0A1018 100%);
        border: 1px solid rgba(0,196,159,0.15);
        border-radius: 14px;
        padding: 1.4rem 1.2rem 1.2rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .kec-hero-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00C49F, transparent);
        opacity: 0.6;
    }
    .kec-hero-card:hover {
        border-color: rgba(0,196,159,0.4);
        box-shadow: 0 10px 35px rgba(0,196,159,0.08);
    }
    .kec-hero-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #4A6070;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.55rem;
    }
    .kec-hero-value {
        font-size: 2.6rem;
        font-weight: 800;
        color: #00C49F;
        letter-spacing: -0.04em;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }
    .kec-hero-sub {
        font-size: 0.73rem;
        color: #445566;
        margin-top: 0.5rem;
        line-height: 1.45;
    }
    .kec-hero-trend {
        font-size: 0.71rem;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    /* Indicator grid */
    .kec-indicator-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    .kec-indicator-card {
        background: linear-gradient(145deg, #141B28 0%, #111620 100%);
        border: 1px solid #1E2738;
        border-radius: 12px;
        padding: 1.3rem 1.4rem;
        transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
    }
    .kec-indicator-card:hover {
        border-color: rgba(0,196,159,0.35);
        box-shadow: 0 8px 28px rgba(0,196,159,0.07);
        transform: translateY(-2px);
    }
    .kec-ind-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }
    .kec-ind-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #7A9AB0;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    .kec-ind-source {
        font-size: 0.64rem;
        color: #3A4A58;
    }
    .kec-ind-value {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
    }
    .kec-ind-trend {
        font-size: 0.72rem;
        font-weight: 600;
        color: #00C49F;
        margin-top: 0.2rem;
    }
    .kec-ind-explain {
        font-size: 0.8rem;
        color: #8899AA;
        line-height: 1.55;
        margin-top: 0.65rem;
        border-top: 1px solid #1E2738;
        padding-top: 0.65rem;
    }
    .kec-ind-why {
        font-size: 0.77rem;
        color: #556677;
        line-height: 1.5;
        margin-top: 0.5rem;
        font-style: italic;
    }
    .kec-target {
        display: inline-block;
        font-size: 0.65rem;
        background: rgba(0,196,159,0.07);
        border: 1px solid rgba(0,196,159,0.18);
        border-radius: 4px;
        padding: 0.15rem 0.5rem;
        color: #00C49F;
        margin-top: 0.35rem;
        font-weight: 500;
    }

    /* Why Kenya Matters */
    .kec-why-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.2rem 0;
    }
    .kec-why-card {
        background: linear-gradient(145deg, #0F1824 0%, #0A1018 100%);
        border: 1px solid #1A2436;
        border-radius: 12px;
        padding: 1.3rem;
        transition: border-color 0.25s ease, transform 0.25s ease;
    }
    .kec-why-card:hover {
        border-color: rgba(0,196,159,0.3);
        transform: translateY(-3px);
    }
    .kec-why-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
    .kec-why-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #DDE8F4;
        margin-bottom: 0.4rem;
    }
    .kec-why-body {
        font-size: 0.8rem;
        color: #8899AA;
        line-height: 1.55;
    }

    /* Personal research section */
    .kec-research-card {
        background: linear-gradient(145deg, #141B28 0%, #111620 100%);
        border: 1px solid #1E2738;
        border-left: 3px solid #00C49F;
        border-radius: 0 12px 12px 0;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .kec-research-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #DDE8F4;
        margin-bottom: 0.5rem;
    }
    .kec-research-body {
        font-size: 0.83rem;
        color: #8899AA;
        line-height: 1.6;
    }
    .kec-research-concept {
        display: inline-block;
        font-size: 0.65rem;
        color: #00C49F;
        border: 1px solid rgba(0,196,159,0.25);
        border-radius: 4px;
        padding: 0.12rem 0.45rem;
        margin-top: 0.4rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* Section header rule */
    .kec-section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2.4rem 0 1.2rem;
    }
    .kec-section-header-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(0,196,159,0.3), transparent);
    }
    .kec-section-header-text {
        font-size: 0.68rem;
        font-weight: 700;
        color: #00C49F;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        white-space: nowrap;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .kec-hero-grid { grid-template-columns: repeat(2, 1fr); }
        .kec-indicator-grid { grid-template-columns: 1fr; }
        .kec-why-grid { grid-template-columns: 1fr; }
        .kec-hero-value { font-size: 2rem; }
        .kec-ind-value { font-size: 1.7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── DATA ──────────────────────────────────────────────────────────────────────

indicators  = get_macro_snapshot()
comparisons = get_ssa_comparison()
gdp_hist    = get_gdp_history()
inf_hist    = get_inflation_history()

# ── SCROLLING TICKER ─────────────────────────────────────────────────────────

_TICKER_ITEMS = [
    ('🇰🇪 KENYA INFLATION', '4.0%', False),
    ('CBK POLICY RATE',      '9.75%', False),
    ('GDP GROWTH',           '+5.4%', False),
    ('FINANCIAL INCLUSION',  '83.7%', False),
    ('MOBILE MONEY',         '75.0%', False),
    ('DEBT / GDP',           '68.4%', False),
    ('UNEMPLOYMENT',         '12.7%', True),
    ('YOUTH UNEMPLOYMENT',   '~35%',  True),
    ('POPULATION',           '56.4M', False),
    ('SSA INFLATION AVG',    '14.0%', True),
    ('SSA GDP GROWTH AVG',   '3.5%',  False),
    ('M-PESA TRANSACTIONS',  '$250B/yr', False),
]

def _ticker_html():
    sep = '<span class="kec-ticker-sep">◆</span>'
    items_html = ""
    for label, val, neg in _TICKER_ITEMS:
        cls = "kec-neg" if neg else "kec-val"
        items_html += (
            f'<span class="kec-ticker-item">{label} '
            f'<span class="{cls}">{val}</span></span>'
            f'{sep}'
        )
    # Duplicate for seamless loop
    block = items_html * 2
    return (
        '<div class="kec-ticker-wrapper">'
        '<div class="kec-ticker-inner">'
        + block +
        '</div></div>'
    )

st.markdown(_ticker_html(), unsafe_allow_html=True)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    """
    <div style="margin-top:1.8rem; margin-bottom:0.4rem;">
        <span style="font-size:0.68rem; font-weight:700; color:#00C49F;
                     text-transform:uppercase; letter-spacing:0.15em;">
            WealthMind Africa &nbsp;·&nbsp; Economic Intelligence
        </span>
    </div>
    <h1 style="font-size:2.5rem; color:#E2E8F0; letter-spacing:-0.035em;
               line-height:1.15; margin:0 0 0.5rem 0;">
        Kenya Economic Context
    </h1>
    <p style="color:#8899AA; font-size:1rem; line-height:1.65;
              max-width:640px; margin:0 0 0.4rem 0;">
        A macroeconomic overview of Kenya — one of Sub-Saharan Africa's most
        structurally interesting economies. Data sourced from
        <strong style="color:#CCDDE8;">KNBS, CBK, World Bank, IMF, and GSMA</strong>.
    </p>
    """,
    unsafe_allow_html=True,
)

# ── HERO ANIMATED COUNTERS ────────────────────────────────────────────────────
# Four headline metrics rendered in an iframe with JavaScript animation.
# Background colour matches Streamlit's dark theme (#0E1117).

_HERO_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    background: #0E1117;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 0.5rem 0;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }
  .card {
    background: linear-gradient(145deg, #0F1824, #0A1018);
    border: 1px solid rgba(0,196,159,0.18);
    border-radius: 14px;
    padding: 1.4rem 1.2rem 1.2rem;
    position: relative;
    overflow: hidden;
  }
  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00C49F, transparent);
    opacity: 0.55;
  }
  .label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #4A6070;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
  }
  .value {
    font-size: 2.55rem;
    font-weight: 800;
    color: #00C49F;
    letter-spacing: -0.04em;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    min-height: 2.6rem;
  }
  .trend {
    font-size: 0.69rem;
    font-weight: 600;
    color: #00C49F;
    margin-top: 0.45rem;
    opacity: 0.75;
  }
  .sub {
    font-size: 0.69rem;
    color: #3A4A58;
    margin-top: 0.25rem;
    line-height: 1.4;
  }
  @media (max-width: 550px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
    .value { font-size: 2rem; }
  }
</style>
</head>
<body>
<div class="grid">
  <div class="card">
    <div class="label">Headline Inflation</div>
    <div class="value" id="v-inf">0.0%</div>
    <div class="trend">↓ Down from 9.6% peak</div>
    <div class="sub">KNBS · May 2025</div>
  </div>
  <div class="card">
    <div class="label">GDP Growth</div>
    <div class="value" id="v-gdp">0.0%</div>
    <div class="trend">→ Above SSA avg 3.5%</div>
    <div class="sub">World Bank · 2024</div>
  </div>
  <div class="card">
    <div class="label">CBK Policy Rate</div>
    <div class="value" id="v-cbk">0.00%</div>
    <div class="trend">↓ Down from 13.0%</div>
    <div class="sub">Central Bank of Kenya · 2025</div>
  </div>
  <div class="card">
    <div class="label">Financial Inclusion</div>
    <div class="value" id="v-fin">0.0%</div>
    <div class="trend">↑ Up from 26.7% in 2006</div>
    <div class="sub">FinAccess Survey · 2021</div>
  </div>
</div>
<script>
function animateCounter(id, target, decimals, suffix, delay) {
    setTimeout(function() {
        var el = document.getElementById(id);
        var duration = 1500;
        var start = performance.now();
        function step(now) {
            var progress = Math.min((now - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = (eased * target).toFixed(decimals) + suffix;
            if (progress < 1) { requestAnimationFrame(step); }
        }
        requestAnimationFrame(step);
    }, delay);
}
animateCounter('v-inf', 4.0,  1, '%',  120);
animateCounter('v-gdp', 5.4,  1, '%',  280);
animateCounter('v-cbk', 9.75, 2, '%',  440);
animateCounter('v-fin', 83.7, 1, '%',  600);
</script>
</body>
</html>
"""

components.html(_HERO_HTML, height=160)

# ── SECTION: GDP + INFLATION TREND CHARTS ────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">Economic Performance Trends</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

ch1, ch2 = st.columns(2)

with ch1:
    years_g  = [d["year"]   for d in gdp_hist]
    values_g = [d["growth"] for d in gdp_hist]

    fig_gdp = go.Figure()
    fig_gdp.add_trace(go.Bar(
        x=years_g, y=values_g,
        marker_color=[
            "#00C49F" if v >= 0 else "#FF4444" for v in values_g
        ],
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>GDP growth: %{y:.1f}%<extra></extra>",
    ))
    fig_gdp.add_hline(y=3.5, line_dash="dash", line_color="#4A6070",
                      annotation_text="SSA avg 3.5%",
                      annotation_font_color="#4A6070",
                      annotation_position="bottom right")
    fig_gdp.update_layout(
        title=dict(text="Kenya Real GDP Growth (%)", font=dict(size=13, color="#CCDDE8"), x=0),
        height=240,
        paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        font=dict(color="#8899AA", size=11),
        xaxis=dict(showgrid=False, color="#4A6070", tickformat="d"),
        yaxis=dict(showgrid=True, gridcolor="#1A2030", color="#4A6070",
                   zeroline=True, zerolinecolor="#2A3040"),
        margin=dict(t=40, b=30, l=45, r=20),
        bargap=0.3,
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

with ch2:
    years_i  = [d["year"] for d in inf_hist]
    values_i = [d["rate"] for d in inf_hist]

    fig_inf = go.Figure()
    fig_inf.add_trace(go.Scatter(
        x=years_i, y=values_i,
        mode="lines+markers",
        line=dict(color="#FF8800", width=2.5),
        marker=dict(size=6, color="#FF8800"),
        fill="tozeroy",
        fillcolor="rgba(255,136,0,0.06)",
        hovertemplate="<b>%{x}</b><br>Inflation: %{y:.1f}%<extra></extra>",
    ))
    fig_inf.add_hrect(y0=2.5, y1=7.5,
                      fillcolor="rgba(0,196,159,0.05)",
                      line_width=0,
                      annotation_text="CBK target band",
                      annotation_font_color="#3A6050",
                      annotation_position="top right")
    fig_inf.update_layout(
        title=dict(text="Kenya Headline Inflation (%)", font=dict(size=13, color="#CCDDE8"), x=0),
        height=240,
        paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        font=dict(color="#8899AA", size=11),
        xaxis=dict(showgrid=False, color="#4A6070", tickformat="d"),
        yaxis=dict(showgrid=True, gridcolor="#1A2030", color="#4A6070"),
        margin=dict(t=40, b=30, l=45, r=20),
    )
    st.plotly_chart(fig_inf, use_container_width=True)

# ── SECTION: 8 INDICATOR CARDS ────────────────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">Key Economic Indicators</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

_TREND_COLOUR = {"up": "#00C49F", "down": "#00C49F", "stable": "#4499FF"}
_TREND_ARROW  = {"up": "↑", "down": "↓", "stable": "→"}

# Render in pairs (2-column grid via Streamlit columns)
for i in range(0, len(indicators), 2):
    left_ind  = indicators[i]
    right_ind = indicators[i + 1] if i + 1 < len(indicators) else None

    col_l, col_r = st.columns(2)

    def _render_card(col, ind):
        tc = _TREND_COLOUR.get(ind["trend"], "#4499FF")
        ta = _TREND_ARROW.get(ind["trend"], "→")
        with col:
            st.markdown(
                f'<div class="kec-indicator-card">'

                f'<div class="kec-ind-header">'
                f'<span class="kec-ind-label">{ind["flag"]} {ind["label"]}</span>'
                f'<span class="kec-ind-source">{ind["source"]}</span>'
                f'</div>'

                f'<div class="kec-ind-value" style="color:{ind["colour"]};">'
                f'{ind["display"]}</div>'

                f'<div class="kec-ind-trend" style="color:{tc};">'
                f'{ta} {ind["trend_label"]}</div>'

                f'<div><span class="kec-target">{ind["target"]}</span></div>'

                f'<div class="kec-ind-explain">{ind["short_explanation"]}</div>'

                f'<div class="kec-ind-why">'
                f'<strong style="color:#4A6070; font-style:normal; font-size:0.65rem;'
                f' text-transform:uppercase; letter-spacing:0.08em;">Why It Matters</strong>'
                f'<br>{ind["why_matters"]}</div>'

                f'</div>',
                unsafe_allow_html=True,
            )

    _render_card(col_l, left_ind)
    if right_ind:
        _render_card(col_r, right_ind)

# ── SECTION: KENYA vs SSA COMPARISON ─────────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">Kenya vs Sub-Saharan Africa</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="color:#8899AA; font-size:0.87rem; line-height:1.6; max-width:660px;'
    ' margin-bottom:1rem;">Kenya exists within a broader regional context. '
    'The comparisons below position Kenya\'s macroeconomic performance against '
    'Sub-Saharan Africa averages — showing where Kenya leads, and where structural '
    'challenges remain.</p>',
    unsafe_allow_html=True,
)

# 2×2 grid of comparison charts
ssa_pairs = [(comparisons[i], comparisons[i+1])
             for i in range(0, len(comparisons), 2)]

for pair in ssa_pairs:
    c1, c2 = st.columns(2)
    for col, comp in zip([c1, c2], pair):
        # Kenya always teal; SSA muted blue-grey
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[comp["kenya"], comp["ssa"]],
            y=["Kenya", "SSA Avg"],
            orientation="h",
            marker_color=["#00C49F", "#2A4055"],
            marker_line_width=0,
            text=[comp["kenya_label"], comp["ssa_label"]],
            textposition="outside",
            textfont=dict(size=11, color=["#00C49F", "#4A6070"]),
            hovertemplate="%{y}: %{x:.1f}" + comp["unit"] + "<extra></extra>",
            width=0.45,
        ))
        fig.update_layout(
            title=dict(
                text=comp["metric"],
                font=dict(size=12, color="#CCDDE8"),
                x=0,
            ),
            height=160,
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#8899AA", size=10),
            xaxis=dict(
                showgrid=True, gridcolor="#1A2030",
                color="#4A6070",
                range=[0, max(comp["kenya"], comp["ssa"]) * 1.35],
            ),
            yaxis=dict(showgrid=False, color="#7A9AB0"),
            margin=dict(t=35, b=10, l=60, r=70),
            showlegend=False,
            bargap=0.4,
        )
        with col:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f'<p style="font-size:0.75rem; color:#4A6070; line-height:1.5;'
                f' margin-top:-0.6rem; margin-bottom:0.8rem;">'
                f'{comp["note"]}'
                f' <span style="color:#2A3A48;">— {comp["source"]}</span></p>',
                unsafe_allow_html=True,
            )

# ── SECTION: WHY KENYA MATTERS ────────────────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">Why Kenya Matters</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="color:#8899AA; font-size:0.9rem; line-height:1.65; max-width:680px;'
    ' margin-bottom:1.4rem;">'
    'Kenya is not simply another emerging market. It is one of the most economically '
    'interesting laboratories in the world — combining rapid fintech innovation, a '
    'structurally young population, and a development economics story that challenges '
    'conventional assumptions about how financial systems evolve.</p>',
    unsafe_allow_html=True,
)

_WHY_CARDS = [
    {
        "icon": "📱",
        "title": "Mobile Money Leadership",
        "body": (
            "M-Pesa, launched by Safaricom in 2007, gave Kenya a 15-year head start "
            "on the rest of the world in mobile-first financial services. Over KES 36 "
            "trillion flows through M-Pesa annually — a parallel financial system built "
            "on telecoms infrastructure instead of bank branches."
        ),
    },
    {
        "icon": "🏦",
        "title": "Financial Inclusion Leap",
        "body": (
            "Kenya raised financial inclusion from 26.7% (2006) to 83.7% (2021) in 15 "
            "years — one of the fastest gains in development history. Suri & Jack (2016) "
            "estimated that M-Pesa alone lifted 2% of Kenyan households out of poverty, "
            "primarily by enabling consumption smoothing across income shocks."
        ),
    },
    {
        "icon": "🚀",
        "title": "Fintech Innovation Hub",
        "body": (
            "Nairobi's 'Silicon Savannah' hosts Africa's largest concentration of "
            "fintech startups. Innovations like M-Shwari (micro-credit), M-Akiba "
            "(retail government bonds via mobile), and digital insurance products are "
            "solutions to real development economics problems — not copies of Western fintech."
        ),
    },
    {
        "icon": "👥",
        "title": "Youth Demographic",
        "body": (
            "With a median age of 19, Kenya's population is overwhelmingly young. "
            "This creates both a demographic dividend — a large future workforce — and "
            "a structural challenge: the economy must create formal employment for "
            "~800,000 new labour market entrants every year to realise that dividend."
        ),
    },
    {
        "icon": "🌱",
        "title": "Entrepreneurship Culture",
        "body": (
            "Kenya's informal sector — jua kali — employs ~83% of the workforce and "
            "reflects deep entrepreneurial resilience. The World Bank ranks Kenya 56th "
            "globally for ease of doing business (2020). The tech startup ecosystem "
            "has produced unicorns including Flutterwave and Andela with Kenyan roots."
        ),
    },
    {
        "icon": "🌍",
        "title": "Regional Economic Influence",
        "body": (
            "Nairobi is the economic capital of East Africa. Kenya's port of Mombasa "
            "serves Uganda, Rwanda, South Sudan, and DRC. The NSE is East Africa's "
            "largest securities exchange. Kenya's macroeconomic stability — relative "
            "to neighbours — makes it the region's anchor economy and a test case for "
            "development economics models."
        ),
    },
]

# 3-column grid
_WHY_HTML = '<div class="kec-why-grid">'
for card in _WHY_CARDS:
    _WHY_HTML += (
        f'<div class="kec-why-card">'
        f'<div class="kec-why-icon">{card["icon"]}</div>'
        f'<div class="kec-why-title">{card["title"]}</div>'
        f'<div class="kec-why-body">{card["body"]}</div>'
        f'</div>'
    )
_WHY_HTML += '</div>'
st.markdown(_WHY_HTML, unsafe_allow_html=True)

# ── SECTION: WHAT I FOUND INTERESTING ────────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">What I Found Interesting</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="color:#8899AA; font-size:0.88rem; line-height:1.6; max-width:660px;'
    ' margin-bottom:1.4rem;">'
    'These are the questions that genuinely surprised me while researching Kenya\'s '
    'economic environment — the moments where the data challenged what I expected.'
    ' — <em style="color:#4A6070;">Yash Karia</em></p>',
    unsafe_allow_html=True,
)

_RESEARCH_ITEMS = [
    {
        "title": "Inflation hits the poor hardest — and not in the way people expect",
        "concept": "Engel's Law · CPI Composition",
        "body": (
            "I expected inflation to affect everyone roughly equally. The data showed "
            "something more nuanced: Kenya's CPI weights food at ~36%, but low-income "
            "households spend 55–60% of income on food (KNBS, 2021). When food inflation "
            "hit 12.4% in mid-2023, the effective inflation rate for lower-income households "
            "was substantially higher than the headline 9.6%. This is Engel's Law in action — "
            "as income rises, the share spent on food falls, making inflation less regressive "
            "at higher income levels. The implication for policymakers is significant: "
            "headline CPI understates the welfare cost of food price shocks for the poor."
        ),
    },
    {
        "title": "Present bias is not just a personal flaw — it is a policy problem",
        "concept": "Laibson (1997) · Behavioural Economics · Commitment Devices",
        "body": (
            "Laibson's hyperbolic discounting model shows that people consistently "
            "overvalue immediate consumption relative to future welfare — even when they "
            "know they are doing so. What I found striking was the policy dimension: "
            "M-Akiba and M-Shwari are not just financial products, they are commitment "
            "devices that exploit the same mobile-payment infrastructure to help people "
            "overcome their own present bias. The most effective financial inclusion "
            "tools do not just provide access — they redesign the choice architecture "
            "around a known behavioural bias."
        ),
    },
    {
        "title": "Financial inclusion is not binary — there is a spectrum that matters",
        "concept": "FinAccess Framework · Formal vs Informal Finance",
        "body": (
            "I initially treated 'financial inclusion' as a binary: included or excluded. "
            "The FinAccess framework reveals a richer picture: 83.7% broad inclusion "
            "versus 56.8% formal inclusion — a 27-percentage-point gap representing "
            "millions of Kenyans who rely on mobile wallets but lack access to credit, "
            "insurance, or investment products. The distinction matters because mobile "
            "money enables consumption smoothing but not capital accumulation. A farmer "
            "with M-Pesa can smooth income across seasons but cannot access the long-term "
            "capital needed to invest in irrigation or equipment."
        ),
    },
    {
        "title": "M-Pesa is not a fintech story — it is a development economics story",
        "concept": "Suri & Jack (2016) · Technology and Poverty Reduction",
        "body": (
            "The conventional narrative frames M-Pesa as a technology success. "
            "Suri & Jack's 2016 study in Science reframes it as a development economics "
            "result: access to mobile money increased household consumption by 2% on average, "
            "and lifted 2% of Kenyan households out of poverty — predominantly female-headed "
            "households. The mechanism was consumption smoothing: M-Pesa allowed households "
            "to receive remittances from urban family members immediately after a shock "
            "(illness, drought, job loss) rather than waiting for physical cash transfer. "
            "The welfare gain came not from investment, but from risk-sharing."
        ),
    },
]

for item in _RESEARCH_ITEMS:
    st.markdown(
        f'<div class="kec-research-card">'
        f'<div class="kec-research-title">{item["title"]}</div>'
        f'<div class="kec-research-body">{item["body"]}</div>'
        f'<span class="kec-research-concept">{item["concept"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── SIGN-IN CTA ───────────────────────────────────────────────────────────────

st.markdown(
    '<div class="kec-section-header">'
    '<span class="kec-section-header-text">Apply This Context To Your Own Data</span>'
    '<div class="kec-section-header-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="background:linear-gradient(145deg,#0F1824,#0A1018);'
    ' border:1px solid rgba(0,196,159,0.2); border-radius:14px;'
    ' padding:2rem 2.2rem; max-width:640px; margin-bottom:1.5rem;">'
    '<div style="font-size:1.15rem; font-weight:700; color:#E2E8F0;'
    ' margin-bottom:0.6rem;">See how Kenya\'s macro environment affects you</div>'
    '<div style="font-size:0.85rem; color:#8899AA; line-height:1.6; margin-bottom:1.2rem;">'
    'Create a free account to apply Kenya\'s real inflation data to your personal '
    'spending — distinguishing nominal changes from real ones using the Fisher equation. '
    'Analyse your savings rate, detect present bias in your spending, and project '
    'your wealth trajectory over 25 years.</div>'
    '<div style="font-size:0.75rem; color:#3A4A58;">Free · No card required · Built for Kenya</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.page_link("app.py", label="→ Create an account or sign in")

# ── SOURCES ───────────────────────────────────────────────────────────────────

with st.expander("📚 Data Sources & Methodology", expanded=False):
    st.markdown(
        """
        All macroeconomic data on this page is sourced from official and peer-reviewed
        publications. Where figures are estimates or projections, this is noted.

        **Primary Sources:**
        - Kenya National Bureau of Statistics (KNBS). *Consumer Price Index Monthly Reports.* 2024–2025.
        - Central Bank of Kenya (CBK) / KNBS / FSD Kenya. *FinAccess Household Survey.* 2021.
        - World Bank. *World Development Indicators.* 2024.
        - International Monetary Fund. *World Economic Outlook.* April 2025.
        - GSMA. *State of the Industry Report on Mobile Money.* 2024.
        - Central Bank of Kenya. *Monetary Policy Committee Statements.* 2025.

        **Academic References:**
        - Suri, T. & Jack, W. (2016). The long-run poverty and gender impacts of mobile money. *Science, 354*(6317), 1288–1292.
        - Dupas, P. & Robinson, J. (2013). Savings constraints and microenterprise development. *AER, 103*(4), 1138–1171.
        - World Bank. (2022). *The Global Findex Database 2021.* World Bank Group.

        **Methodology Note:**
        Sub-Saharan Africa averages are population-weighted means sourced from
        World Bank World Development Indicators and IMF WEO data. Where exact
        SSA averages are unavailable, median-country estimates are used and labeled accordingly.
        All figures reflect data available as of June 2025.
        """
    )

render_footer()
