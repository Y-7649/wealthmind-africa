"""
pages/9_impact.py
WealthMind Africa — School Impact Report

PUBLIC page. No login required. Reads like a behavioural-economics research
briefing on the platform's user cohort.

Honesty model:
    - The cohort headline figures (students, transactions, value) are ALWAYS
      real, drawn live from the database.
    - The behavioural findings are shown live once the cohort reaches
      MIN_PUBLIC_COHORT users. Below that, the page shows clearly-labelled
      ILLUSTRATIVE findings (so the analyses are visible from day one) and
      states plainly that live findings activate automatically as students join.

This is the public, admissions-facing counterpart to the Admin Analytics
Dashboard — same engine (core/analytics.py), aggregate-only, never identifying.

Created by Yash Karia
"""

import streamlit as st
import plotly.graph_objects as go

from core.analytics import get_cohort_analytics, MIN_PUBLIC_COHORT
from utils.styles import inject_global_styles
from utils.footer import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="School Impact Report — WealthMind Africa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_styles()

st.markdown(
    """
    <style>
    .imp-kicker { font-size:0.66rem; font-weight:700; color:#00C49F;
        text-transform:uppercase; letter-spacing:0.17em; margin-bottom:0.5rem; }
    .imp-title { font-size:2.3rem; font-weight:800; color:#E2E8F0;
        letter-spacing:-0.035em; line-height:1.15; margin-bottom:0.5rem; }
    .imp-deck { font-size:1.02rem; color:#8899AA; line-height:1.65;
        max-width:700px; margin-bottom:0.7rem; }
    .imp-byline { font-size:0.75rem; color:#3A4A58; border-top:1px solid #1A2030;
        padding-top:0.6rem; margin-top:0.6rem; }
    .imp-band { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:1.6rem 0; }
    .imp-stat { background:linear-gradient(145deg,#0F1824,#0A1018);
        border:1px solid rgba(0,196,159,0.15); border-radius:14px; padding:1.4rem 1.3rem;
        position:relative; overflow:hidden; }
    .imp-stat::before { content:''; position:absolute; top:0; left:0; right:0; height:2px;
        background:linear-gradient(90deg,transparent,#00C49F,transparent); opacity:0.6; }
    .imp-stat-val { font-size:2.4rem; font-weight:800; color:#00C49F; letter-spacing:-0.04em;
        line-height:1; font-variant-numeric:tabular-nums; }
    .imp-stat-lbl { font-size:0.68rem; font-weight:600; color:#4A6070; text-transform:uppercase;
        letter-spacing:0.1em; margin-top:0.55rem; }
    .imp-finding { background:linear-gradient(145deg,#141B28,#111620); border:1px solid #1E2738;
        border-left:3px solid #00C49F; border-radius:0 12px 12px 0; padding:1.3rem 1.5rem;
        margin-bottom:1rem; }
    .imp-finding-head { font-size:1.05rem; font-weight:700; color:#E2E8F0;
        letter-spacing:-0.015em; line-height:1.3; margin-bottom:0.4rem; }
    .imp-finding-body { font-size:0.85rem; color:#8899AA; line-height:1.6; }
    .imp-concept { display:inline-block; font-size:0.62rem; color:#00C49F;
        border:1px solid rgba(0,196,159,0.22); border-radius:4px; padding:0.13rem 0.5rem;
        margin-top:0.5rem; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; }
    .imp-illus { display:inline-flex; align-items:center; gap:0.4rem; background:rgba(255,136,0,0.08);
        border:1px solid rgba(255,136,0,0.25); border-radius:6px; padding:0.4rem 0.85rem;
        font-size:0.72rem; font-weight:600; color:#CC8800; margin-bottom:1rem; }
    .imp-rule { display:flex; align-items:center; gap:1rem; margin:2.6rem 0 1.6rem; }
    .imp-rule-line { flex:1; height:1px; background:linear-gradient(90deg,rgba(0,196,159,0.25),transparent); }
    .imp-rule-text { font-size:0.64rem; font-weight:700; color:#00C49F; text-transform:uppercase;
        letter-spacing:0.15em; white-space:nowrap; }
    @media (max-width:768px) {
        .imp-title { font-size:1.7rem; }
        .imp-band { grid-template-columns:1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── LOAD ANALYTICS (cached) ───────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner="Compiling cohort report…")
def _load():
    return get_cohort_analytics()

c    = _load()
cur  = c["primary_currency"]
live = c["meets_public_threshold"]

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="imp-kicker">WealthMind Africa &nbsp;·&nbsp; Behavioural Economics Field Report</div>
    <div class="imp-title">School Impact Report</div>
    <div class="imp-deck">
        WealthMind Africa is a behavioural economics study of how people across different
        age groups and life stages in Kenya make financial decisions. Most participants
        take a 2-minute anonymous assessment; some also track their finances over time.
        This report summarises what the platform has measured across that cohort: savings
        behaviour, present bias, financial resilience, and spending composition. All
        figures are anonymised aggregates; no individual is identifiable.
    </div>
    <div class="imp-byline">
        Compiled by <strong style="color:#556677;">Yash Karia</strong>
        &nbsp;·&nbsp; Aggregated, anonymised cohort data
        &nbsp;·&nbsp; <a href="mailto:yashkaria.pro@gmail.com"
            style="color:#3A5060; text-decoration:none;">yashkaria.pro@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── COHORT BAND (always real) ─────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="imp-band">
        <div class="imp-stat">
            <div class="imp-stat-val">{c['participants']['total']:,}</div>
            <div class="imp-stat-lbl">Study Participants</div>
        </div>
        <div class="imp-stat">
            <div class="imp-stat-val">{c['participants']['n_assessment']:,}</div>
            <div class="imp-stat-lbl">Via Quick Assessment</div>
        </div>
        <div class="imp-stat">
            <div class="imp-stat-val">{c['participants']['n_tracking']:,}</div>
            <div class="imp-stat-lbl">Ongoing Tracking</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"{c['participants']['n_assessment']} via the 2-minute assessment · "
    f"{c['participants']['n_tracking']} through ongoing tracking · "
    f"{c['n_transactions']:,} transactions analysed. "
    f"Live behavioural findings activate automatically once {MIN_PUBLIC_COHORT}+ "
    f"participants have contributed."
)

# ── FINDINGS ──────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="imp-rule"><span class="imp-rule-text">Key Findings</span>'
    '<div class="imp-rule-line"></div></div>',
    unsafe_allow_html=True,
)

# Representative ILLUSTRATIVE parameters, used only until the live cohort is
# large enough. These mirror documented patterns in Kenyan household finance and
# behavioural economics literature; they are NOT presented as live user data.
_DEMO = {
    "n_label":          "an illustrative cohort",
    "avg_savings":      11.4,
    "pct_present":      62,
    "avg_bias":         1.34,
    "top_cats_pct":     58,
    "median_ef":        1.8,
    "avg_health":       47,
    "health_values":    [22, 31, 35, 38, 41, 44, 46, 48, 51, 55, 58, 63, 67, 72, 78],
    "savings_values":   [-4, 2, 5, 7, 8, 9, 11, 12, 13, 14, 16, 18, 21, 24, 29],
    "bias_values":      [0.9, 1.0, 1.05, 1.12, 1.2, 1.28, 1.33, 1.36, 1.4, 1.45, 1.5, 1.6, 1.72, 1.85, 2.1],
    "ef_values":        [0.2, 0.5, 0.8, 1.1, 1.4, 1.6, 1.8, 2.0, 2.4, 2.9, 3.2, 3.8, 4.5, 5.6, 7.0],
    "categories":       [("Food", 34), ("Transport", 24), ("Rent", 16),
                         ("Utilities", 9), ("Entertainment", 8), ("Education", 5),
                         ("Health", 3), ("Other", 1)],
}

if not live:
    st.markdown(
        f'<div class="imp-illus">⚠ Illustrative findings — live cohort findings activate at '
        f'{MIN_PUBLIC_COHORT}+ students. The figures below show the exact analyses the platform runs.</div>',
        unsafe_allow_html=True,
    )

def finding(head, body, concept):
    st.markdown(
        f'<div class="imp-finding"><div class="imp-finding-head">{head}</div>'
        f'<div class="imp-finding-body">{body}</div>'
        f'<span class="imp-concept">{concept}</span></div>',
        unsafe_allow_html=True,
    )

if live:
    h, b, r = c["health"], c["bias"], c["resilience"]
    cats = c["categories"]
    top2_pct = (cats[0]["pct"] + cats[1]["pct"]) if len(cats) >= 2 else 0
    top2_names = " and ".join(x["category"].replace("_", " ") for x in cats[:2]) if len(cats) >= 2 else "—"

    finding(
        f"The average savings rate across the cohort is {h['avg_savings_rate']:.1f}%.",
        f"Measured across {h['n_scored']} participants with sufficient data, against "
        f"the 20% benchmark implied by Friedman's permanent-income hypothesis. "
        f"Median savings rate: {h['median_savings_rate']:.1f}%.",
        "Permanent Income Hypothesis · Friedman (1957)",
    )
    finding(
        f"{b['pct_present_bias']:.0f}% of measured participants exhibit present bias.",
        f"Across {b['n_measured']} participants, the cohort's average present-bias index is "
        f"{b['avg_index']:.2f}. This is a direct, observable trace of hyperbolic "
        f"discounting in self-reported and recorded spending behaviour.",
        "Hyperbolic Discounting · Laibson (1997)",
    )
    if len(cats) >= 2:
        finding(
            f"{top2_names.capitalize()} account for {top2_pct:.0f}% of all recorded spending.",
            "The cohort's revealed consumption basket concentrates in a few categories — "
            "echoing the food-and-transport weighting of Kenya's national CPI basket.",
            "Consumption Composition · KNBS CPI",
        )
    finding(
        f"The median emergency fund covers {r['median_months']:.1f} months of expenses.",
        f"{r['pct_below_3m']:.0f}% of participants fall below the 3-month buffer that Deaton's (1991) "
        f"buffer-stock theory treats as the minimum shock absorber — a measurable financial-resilience gap.",
        "Buffer Stock Theory · Deaton (1991)",
    )
    finding(
        f"The average Financial Health Score is {h['avg_overall']:.0f}/100.",
        "A composite index combining savings rate, emergency fund, spending consistency and "
        "investment commitment — built the way the World Bank's HDI and IMF soundness indicators "
        "combine weighted sub-scores.",
        "Composite Indexing",
    )
else:
    d = _DEMO
    finding(
        f"The average savings rate across {d['n_label']} is {d['avg_savings']:.1f}%.",
        "Measured against the 20% benchmark implied by Friedman's permanent-income hypothesis. "
        "Most students save well below the level associated with long-run wealth accumulation.",
        "Permanent Income Hypothesis · Friedman (1957)",
    )
    finding(
        f"{d['pct_present']}% of students exhibit measurable present bias.",
        f"The illustrative cohort's average present-bias index is {d['avg_bias']:.2f} — first-week "
        "discretionary spending materially exceeds last-week spending, the observable signature of "
        "hyperbolic discounting.",
        "Hyperbolic Discounting · Laibson (1997)",
    )
    finding(
        f"Food and transport account for {d['top_cats_pct']}% of all recorded spending.",
        "The consumption basket concentrates in essentials — echoing the food-and-transport "
        "weighting of Kenya's national CPI basket, and consistent with Engel's Law at lower incomes.",
        "Consumption Composition · KNBS CPI",
    )
    finding(
        f"The median emergency fund covers only {d['median_ef']:.1f} months of expenses.",
        "Well below the 3-month buffer that Deaton's (1991) buffer-stock theory treats as the minimum "
        "shock absorber — a measurable financial-resilience gap across the cohort.",
        "Buffer Stock Theory · Deaton (1991)",
    )
    finding(
        f"The average Financial Health Score is {d['avg_health']}/100.",
        "A composite index combining savings rate, emergency fund, spending consistency and investment "
        "commitment — built the way the World Bank's HDI and IMF soundness indicators combine sub-scores.",
        "Composite Indexing",
    )

# ── DISTRIBUTION CHARTS ───────────────────────────────────────────────────────

st.markdown(
    '<div class="imp-rule"><span class="imp-rule-text">Cohort Distributions</span>'
    '<div class="imp-rule-line"></div></div>',
    unsafe_allow_html=True,
)

PLOTLY_BG = "#0E1117"

def _style(fig, title, height=250):
    fig.update_layout(
        title=dict(text=title, font=dict(size=12.5, color="#CCDDE8"), x=0),
        height=height, paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
        font=dict(color="#8899AA", size=11), showlegend=False,
        margin=dict(t=38, b=32, l=48, r=18),
    )
    fig.update_xaxes(showgrid=False, color="#4A6070")
    fig.update_yaxes(showgrid=True, gridcolor="#1A2030", color="#4A6070")
    return fig

# Choose data source: live or illustrative
if live:
    health_vals  = c["health"]["score_values"]
    savings_vals = c["health"]["savings_values"]
    bias_vals    = c["bias"]["index_values"]
    cats_pairs   = [(x["category"].replace("_", " ").title(), x["pct"]) for x in c["categories"][:8]]
    avg_savings  = c["health"]["avg_savings_rate"]
else:
    health_vals  = _DEMO["health_values"]
    savings_vals = _DEMO["savings_values"]
    bias_vals    = _DEMO["bias_values"]
    cats_pairs   = _DEMO["categories"]
    avg_savings  = _DEMO["avg_savings"]

cc1, cc2 = st.columns(2)

with cc1:
    if savings_vals:
        fig = go.Figure(go.Histogram(x=savings_vals, nbinsx=10,
            marker_color="#00C49F", marker_line_width=0,
            hovertemplate="%{x}% savings<br>%{y} participants<extra></extra>"))
        fig.add_vline(x=20, line_dash="dash", line_color="#7BC8A4",
                      annotation_text="20% benchmark", annotation_font_color="#7BC8A4")
        st.plotly_chart(_style(fig, "Savings Rate Distribution"), use_container_width=True)

with cc2:
    if bias_vals:
        fig = go.Figure(go.Histogram(x=bias_vals, nbinsx=12,
            marker_color="#FF8800", marker_line_width=0,
            hovertemplate="Index %{x}<br>%{y} participants<extra></extra>"))
        fig.add_vline(x=1.1, line_dash="dash", line_color="#FFCC00",
                      annotation_text="bias threshold", annotation_font_color="#FFCC00")
        st.plotly_chart(_style(fig, "Present Bias Index Distribution"), use_container_width=True)

cc3, cc4 = st.columns(2)

with cc3:
    if health_vals:
        fig = go.Figure(go.Histogram(x=health_vals, nbinsx=10,
            marker_color="#4499FF", marker_line_width=0,
            hovertemplate="Score %{x}<br>%{y} participants<extra></extra>"))
        st.plotly_chart(_style(fig, "Financial Health Score Distribution"), use_container_width=True)

with cc4:
    if cats_pairs:
        top = cats_pairs[::-1]
        fig = go.Figure(go.Bar(
            x=[p for _, p in top], y=[n for n, _ in top], orientation="h",
            marker_color="#00C49F", marker_line_width=0,
            text=[f"{p:.0f}%" for _, p in top], textposition="outside",
            textfont=dict(color="#7A9AB0", size=10),
            hovertemplate="%{y}: %{x:.0f}%<extra></extra>"))
        fig.update_layout(
            title=dict(text="Spending by Category", font=dict(size=12.5, color="#CCDDE8"), x=0),
            height=250, paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
            font=dict(color="#8899AA", size=11), showlegend=False,
            margin=dict(t=38, b=32, l=95, r=45),
            xaxis=dict(showgrid=True, gridcolor="#1A2030", color="#4A6070", ticksuffix="%"),
            yaxis=dict(showgrid=False, color="#7A9AB0"))
        st.plotly_chart(fig, use_container_width=True)

# ── LIFE-STAGE COMPARISON (the cross-group finding) ──────────────────────────
# Demographics exist only for assessment respondents; groups below the floor are
# already filtered out in core/analytics.py. Shown only when the cohort is live
# and at least two groups qualify.
_ls = c.get("demographics", {}).get("by_life_stage", [])
if live and len(_ls) >= 2:
    st.markdown(
        '<div class="imp-rule"><span class="imp-rule-text">Across Life Stages</span>'
        '<div class="imp-rule-line"></div></div>',
        unsafe_allow_html=True,
    )
    _hi = max(_ls, key=lambda g: g["avg_bias"])
    _lo = min(_ls, key=lambda g: g["avg_bias"])
    if _hi["group"] != _lo["group"]:
        finding(
            f"Present bias is higher among {_hi['group'].lower()}s than {_lo['group'].lower()}s.",
            f"{_hi['group']}s show an average present-bias index of {_hi['avg_bias']:.2f} "
            f"(n={_hi['n']}), versus {_lo['avg_bias']:.2f} for {_lo['group'].lower()}s "
            f"(n={_lo['n']}) — consistent with the life-cycle view that financial "
            f"self-control develops alongside income stability. Groups with fewer than "
            f"{c['demographics']['min_group']} participants are not shown.",
            "Life-Cycle Hypothesis · Laibson (1997)",
        )
    fig = go.Figure(go.Bar(
        x=[g["group"] for g in _ls], y=[g["avg_bias"] for g in _ls],
        marker_color="#FF8800", marker_line_width=0,
        text=[f"{g['avg_bias']:.2f}" for g in _ls], textposition="outside",
        textfont=dict(color="#7A9AB0", size=11),
        hovertemplate="%{x}: index %{y:.2f}<extra></extra>"))
    st.plotly_chart(_style(fig, "Average Present-Bias Index by Life Stage"),
                    use_container_width=True)

# ── METHODOLOGY + CTA ─────────────────────────────────────────────────────────

with st.expander("📋 Methodology & Data Ethics", expanded=False):
    st.markdown(
        f"""
        **Sample.** This report aggregates every registered user of WealthMind Africa.
        The cohort headline figures (students, transactions, value analysed) are drawn
        live from the database. Behavioural findings are computed by the same engines that
        power each user's private analysis (`core/health_score.py`, `core/present_bias.py`).

        **Anonymity.** Only aggregates are ever displayed. No usernames, balances, or
        individual records appear on this page. Behavioural findings are withheld until the
        cohort reaches **{MIN_PUBLIC_COHORT} students**, below which aggregates could
        approximate an individual — at which point clearly-labelled *illustrative* figures
        are shown instead, so the analyses remain visible without overstating the evidence.

        **Definitions.**
        - *Savings rate*: net monthly saving ÷ income, averaged over up to six months.
        - *Present bias index*: first-week ÷ last-week discretionary spending (Laibson, 1997).
          "Measurable present bias" = index ≥ 1.1.
        - *Emergency fund*: current balance ÷ average monthly expenses (Deaton, 1991).
        - *Financial Health Score*: weighted composite (savings 35%, emergency fund 30%,
          consistency 20%, commitment 15%).

        **References.** Friedman (1957); Hall (1978); Deaton (1991); Laibson (1997);
        O'Donoghue & Rabin (1999); Suri & Jack (2016); KNBS CPI; CBK FinAccess (2021).
        """
    )

st.markdown(
    '<div class="imp-rule"><span class="imp-rule-text">Join the Study</span>'
    '<div class="imp-rule-line"></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="background:linear-gradient(145deg,#0F1824,#0A1018);
                border:1px solid rgba(0,196,159,0.2); border-radius:14px;
                padding:1.8rem 2rem; max-width:620px; margin-bottom:1.4rem;">
        <div style="font-size:1.1rem; font-weight:700; color:#E2E8F0; margin-bottom:0.5rem;">
            Every account added strengthens the study.
        </div>
        <div style="font-size:0.85rem; color:#8899AA; line-height:1.6;">
            When you record your own income and expenses, your anonymised data joins this
            cohort — making the behavioural findings more robust and the platform a richer
            applied-economics study.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.page_link("app.py", label="→ Create an account or sign in")

render_footer()
