"""
pages/2_health_score.py
WealthMind Africa — Financial Health Score

Displays the composite Financial Health Score and its four sub-dimensions.
Each sub-score is explained in plain language with its economic foundation.
A trend chart shows how the score changes over time.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from core.health_score import calculate_health_score
from database.db import save_health_snapshot, get_health_snapshot_history
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Financial Health Score — WealthMind Africa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── AUTH GUARD ────────────────────────────────────────────────────────────────

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="← Go to Login")
    st.stop()

user     = st.session_state.user
user_id  = user["id"]
currency = user.get("currency", "KES")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

render_sidebar("health_score")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── CALCULATE SCORE ───────────────────────────────────────────────────────────

scores = calculate_health_score(user_id)

# Save a snapshot every time this page is visited — builds the trend history
save_health_snapshot(user_id, scores)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#00C49F;'>📊 Financial Health Score</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "A composite index measuring your financial position across four dimensions, "
    "each grounded in economic and financial theory."
)
st.divider()

# ── NO DATA STATE ─────────────────────────────────────────────────────────────

if not scores["has_sufficient_data"]:
    st.info(
        "📋 **More data needed.**  \n"
        "Record at least one month of income and expenses on the "
        "**Transactions** page to generate your Financial Health Score.  \n\n"
        f"Data recorded so far: {scores['months_of_data']} month(s)."
    )
    st.page_link("pages/1_dashboard.py", label="→ Go to Transactions")
    st.stop()

# ── OVERALL SCORE GAUGE ───────────────────────────────────────────────────────

overall = scores["overall_score"]

# Determine colour based on score band
if overall >= 70:
    gauge_colour = "#00C49F"   # Green
    band_label   = "Strong"
elif overall >= 40:
    gauge_colour = "#FF8800"   # Amber
    band_label   = "Developing"
else:
    gauge_colour = "#FF4444"   # Red
    band_label   = "Needs Attention"

_, gauge_col, _ = st.columns([1, 2, 1])

with gauge_col:
    fig_gauge = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = overall,
        title = {"text": f"Overall Score — {band_label}", "font": {"size": 18}},
        number= {"font": {"size": 52, "color": gauge_colour}},
        gauge = {
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#AAAAAA",
            },
            "bar": {"color": gauge_colour, "thickness": 0.3},
            "bgcolor": "#1C2333",
            "steps": [
                {"range": [0,  40], "color": "#2A1A1A"},
                {"range": [40, 70], "color": "#2A2010"},
                {"range": [70, 100], "color": "#0A2A20"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": overall,
            },
        },
    ))

    fig_gauge.update_layout(
        height=300,
        margin=dict(t=40, b=0, l=30, r=30),
        paper_bgcolor="#0E1117",
        font={"color": "#FAFAFA"},
    )

    st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# ── FOUR SUB-SCORE CARDS ──────────────────────────────────────────────────────

st.markdown("### Score Breakdown")
st.caption(
    "Each dimension corresponds to a named concept in personal finance "
    "and macroeconomic theory."
)

c1, c2, c3, c4 = st.columns(4)

def score_colour(s):
    if s >= 70: return "#00C49F"
    elif s >= 40: return "#FF8800"
    else: return "#FF4444"

def score_band(s):
    if s >= 70: return "Strong"
    elif s >= 40: return "Developing"
    else: return "Needs Attention"

with c1:
    s = scores["savings_rate_score"]
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-top: 3px solid {score_colour(s)};'>
            <div style='font-size:2rem; font-weight:bold;
                        color:{score_colour(s)};'>{s:.0f}</div>
            <div style='font-size:0.9rem; color:#AAAAAA;'>/100</div>
            <div style='font-weight:bold; margin:0.5rem 0;'>💰 Savings Rate</div>
            <div style='font-size:0.85rem;'>
                Your rate: <strong>{scores['savings_rate_pct']:.1f}%</strong><br>
                Target: 20%+<br>
                Band: {score_band(s)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    s = scores["emergency_fund_score"]
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-top: 3px solid {score_colour(s)};'>
            <div style='font-size:2rem; font-weight:bold;
                        color:{score_colour(s)};'>{s:.0f}</div>
            <div style='font-size:0.9rem; color:#AAAAAA;'>/100</div>
            <div style='font-weight:bold; margin:0.5rem 0;'>🛡️ Emergency Fund</div>
            <div style='font-size:0.85rem;'>
                Coverage: <strong>{scores['emergency_fund_months']:.1f} months</strong><br>
                Target: 3–6 months<br>
                Band: {score_band(s)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    s = scores["consistency_score"]
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-top: 3px solid {score_colour(s)};'>
            <div style='font-size:2rem; font-weight:bold;
                        color:{score_colour(s)};'>{s:.0f}</div>
            <div style='font-size:0.9rem; color:#AAAAAA;'>/100</div>
            <div style='font-weight:bold; margin:0.5rem 0;'>📏 Consistency</div>
            <div style='font-size:0.85rem;'>
                Variability (CV): <strong>{scores['spending_cv']:.3f}</strong><br>
                Target: below 0.15<br>
                Band: {score_band(s)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    s = scores["commitment_score"]
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-top: 3px solid {score_colour(s)};'>
            <div style='font-size:2rem; font-weight:bold;
                        color:{score_colour(s)};'>{s:.0f}</div>
            <div style='font-size:0.9rem; color:#AAAAAA;'>/100</div>
            <div style='font-weight:bold; margin:0.5rem 0;'>📈 Commitment</div>
            <div style='font-size:0.85rem;'>
                Your rate: <strong>{scores['commitment_rate_pct']:.1f}%</strong><br>
                Target: 5%+<br>
                Band: {score_band(s)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── SCORE TREND ───────────────────────────────────────────────────────────────

history = get_health_snapshot_history(user_id, limit=30)

if len(history) >= 2:
    st.markdown("### Score Trend")
    st.caption("Your Financial Health Score over time. Updates each time you visit this page.")

    dates  = [h["snapshot_date"] for h in history]
    scores_over_time = [h["overall_score"] for h in history]

    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=dates,
        y=scores_over_time,
        mode="lines+markers",
        name="Health Score",
        line=dict(color="#00C49F", width=2),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(0,196,159,0.1)",
    ))

    fig_trend.add_hline(y=70, line_dash="dash", line_color="#00aa44",
                        annotation_text="Strong (70)", annotation_position="right")
    fig_trend.add_hline(y=40, line_dash="dash", line_color="#FF8800",
                        annotation_text="Developing (40)", annotation_position="right")

    fig_trend.update_layout(
        height=280,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#FAFAFA"),
        xaxis=dict(showgrid=False, color="#AAAAAA"),
        yaxis=dict(showgrid=True, gridcolor="#2A2A3A", range=[0, 100], color="#AAAAAA"),
        margin=dict(t=20, b=40, l=40, r=80),
    )

    st.plotly_chart(fig_trend, use_container_width=True)
    st.divider()

# ── ECONOMIC EXPLANATIONS ─────────────────────────────────────────────────────

st.markdown("### The Economics Behind Each Dimension")

with st.expander("💰 Savings Rate — Friedman's Permanent Income Hypothesis", expanded=False):
    st.markdown(
        """
        **What it measures:** The percentage of your monthly income that you do not spend.

        **Economic basis:** Milton Friedman's Permanent Income Hypothesis (1957) argues
        that rational consumers base their spending on their *permanent* (long-run average)
        income rather than their current income. A stable, positive savings rate is the
        observable signature of this behaviour — the agent is consistently setting aside
        resources for the future rather than consuming everything available today.

        **Why 20% is the target:** The 20% savings rate benchmark comes from financial
        planning research and aligns with the savings rates observed in households that
        successfully build wealth over multi-decade horizons. Countries with high national
        savings rates — South Korea, Singapore — consistently show stronger long-run
        growth, mirroring the individual-level effect.

        **Your score:** {rate}% → {score}/100
        """.format(
            rate=scores["savings_rate_pct"],
            score=scores["savings_rate_score"],
        )
    )

with st.expander("🛡️ Emergency Fund — Buffer Stock Saving Theory", expanded=False):
    st.markdown(
        """
        **What it measures:** How many months of your average expenses are covered by
        your current liquid balance.

        **Economic basis:** Deaton (1991) and Carroll (1997) developed buffer stock
        saving theory to explain why households maintain liquid savings even when
        investing would yield higher returns. The answer: insurance against income
        shocks. Without a buffer, an unexpected expense or period of unemployment
        forces the household to take on costly debt, disrupting consumption.

        **The 3–6 month standard:** This range is recommended by financial regulators
        in Kenya (CBK) and internationally (FCA, SEC). Below 3 months, a single
        income disruption threatens the household's ability to meet obligations.
        Above 6 months, the opportunity cost of holding idle cash becomes significant.

        **Your score:** {months} months covered → {score}/100
        """.format(
            months=scores["emergency_fund_months"],
            score=scores["emergency_fund_score"],
        )
    )

with st.expander("📏 Spending Consistency — Consumption Smoothing", expanded=False):
    st.markdown(
        """
        **What it measures:** How stable your monthly spending is, measured by the
        Coefficient of Variation (CV = standard deviation ÷ mean). Lower CV = higher score.

        **Economic basis:** Consumption smoothing is a central prediction of the permanent
        income hypothesis and life-cycle models. Hall (1978) showed that rational consumers
        should smooth consumption across time — spending should be relatively stable even
        when income fluctuates. High variability in spending suggests either income
        shocks, impulsive spending behaviour, or present bias (see the Present Bias module).

        **The CV metric:** A CV of 0.1 means your monthly spending varies by about 10%
        of the average — quite consistent. A CV of 0.5 means it varies by 50% — highly
        erratic. Credit analysts use similar metrics to assess household financial stability.

        **Your score:** CV = {cv} → {score}/100
        """.format(
            cv=scores["spending_cv"],
            score=scores["consistency_score"],
        )
    )

with st.expander("📈 Investment Commitment — Capital Accumulation", expanded=False):
    st.markdown(
        """
        **What it measures:** The percentage of your income deliberately transferred
        to savings or investment accounts (recorded under the *savings_transfer* category).

        **Economic basis:** The Solow growth model (1956) identifies capital accumulation
        as the engine of long-run wealth growth. At the individual level, this means
        consistently directing a fraction of income toward assets that generate future
        returns. Even a small, consistent investment rate compounded over decades produces
        dramatically different outcomes — as the Wealth Projection module illustrates.

        **Why the weight is lower (15%):** For young adults, especially students and
        early-career professionals, building the savings habit and emergency fund takes
        priority. Investment commitment becomes increasingly important as income grows.

        **Your score:** {rate}% of income committed → {score}/100
        """.format(
            rate=scores["commitment_rate_pct"],
            score=scores["commitment_score"],
        )
    )

render_footer()
