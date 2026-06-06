"""
pages/3_inflation.py
WealthMind Africa — Kenya Inflation Context

Shows the difference between nominal spending changes (what you see)
and real spending changes (what they mean), adjusted for Kenya's CPI.

Core concept displayed:
    The Fisher equation applied to personal spending data.
    Real change = ((1 + nominal) / (1 + inflation)) - 1
"""

import streamlit as st
import plotly.graph_objects as go

from core.inflation import get_inflation_analysis
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Kenya Inflation Context — WealthMind Africa",
    page_icon="🇰🇪",
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

render_sidebar("inflation")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────

data = get_inflation_analysis(user_id)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#00C49F;'>🇰🇪 Kenya Inflation Context</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Your spending changes shown in **real terms** — adjusted for Kenya's "
    "actual Consumer Price Index — not just nominal figures."
)
st.divider()

# ── NO DATA STATE ─────────────────────────────────────────────────────────────

if not data["has_data"]:
    st.info(
        "📋 **More data needed.**  \n"
        "This module requires at least **2 months** of expense data to "
        "calculate a meaningful comparison.  \n\n"
        f"Months recorded so far: {data.get('months_of_data', 0)}"
    )
    st.page_link("pages/1_dashboard.py", label="→ Go to Transactions")
    st.stop()

# ── KEY METRICS ROW ───────────────────────────────────────────────────────────

headline = data["headline_inflation"]
ssa      = data["ssa_inflation"]
nom      = data["total_nominal_change"]
real     = data["total_real_change"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🇰🇪 Kenya Headline Inflation",
        value=f"{headline * 100:.1f}%",
        help="Current annual CPI — source: KNBS",
    )

with col2:
    st.metric(
        label="🌍 Sub-Saharan Africa Average",
        value=f"{ssa * 100:.1f}%",
        delta=f"Kenya is {(headline - ssa) * 100:.1f}pp {'above' if headline > ssa else 'below'} regional avg",
        delta_color="inverse" if headline > ssa else "normal",
        help="World Bank regional average",
    )

with col3:
    st.metric(
        label=f"📊 Nominal Change ({data['previous_month_label']} → {data['current_month_label']})",
        value=f"{nom * 100:+.1f}%",
        help="Raw percentage change in total spending",
    )

with col4:
    colour_delta = "normal" if real <= nom else "inverse"
    st.metric(
        label="📐 Real Change (inflation-adjusted)",
        value=f"{real * 100:+.1f}%",
        delta="After adjusting for Kenya CPI",
        delta_color="off",
        help="What your spending change means in real consumption terms",
    )

st.divider()

# ── NOMINAL VS REAL CHART ─────────────────────────────────────────────────────

st.markdown("### Nominal vs Real Spending Over Time")
st.caption(
    "Two lines showing the same spending data — once as recorded (nominal), "
    "once deflated by Kenya's CPI (real). The gap between the lines is "
    "the inflation effect."
)

monthly = data["monthly_totals"]

if len(monthly) >= 2:
    labels        = [m["label"]        for m in monthly]
    nominal_vals  = [m["nominal_spend"] for m in monthly]
    real_vals     = [m["real_spend"]    for m in monthly]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=labels, y=nominal_vals,
        name="Nominal Spending",
        mode="lines+markers",
        line=dict(color="#FF8800", width=2),
        marker=dict(size=7),
    ))

    fig.add_trace(go.Scatter(
        x=labels, y=real_vals,
        name="Real Spending (CPI-adjusted)",
        mode="lines+markers",
        line=dict(color="#00C49F", width=2, dash="dash"),
        marker=dict(size=7),
        fill="tonexty",
        fillcolor="rgba(255,136,0,0.08)",
    ))

    fig.update_layout(
        height=320,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#FAFAFA"),
        xaxis=dict(showgrid=False, color="#AAAAAA"),
        yaxis=dict(
            showgrid=True,
            gridcolor="#2A2A3A",
            color="#AAAAAA",
            tickprefix="KES ",
            tickformat=",.0f",
        ),
        legend=dict(bgcolor="#1C2333", bordercolor="#2A2A3A"),
        margin=dict(t=20, b=40, l=60, r=20),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "ℹ️ The shaded area between the lines represents the cumulative "
        "inflation effect. A widening gap means inflation is increasingly "
        "explaining your spending changes rather than genuine consumption growth."
    )

st.divider()

# ── CATEGORY BREAKDOWN ────────────────────────────────────────────────────────

st.markdown("### Category Analysis")
st.caption(
    f"Comparing **{data['previous_month_label']}** to **{data['current_month_label']}**, "
    f"adjusted for Kenya's category-specific inflation rates."
)

cat_data = data["category_analysis"]

if cat_data:
    for category, info in cat_data.items():
        nom_pct  = info["nominal_change"] * 100
        real_pct = info["real_change"]    * 100
        inf_pct  = info["inflation_rate"] * 100

        # Colour the real change: green if decrease, red if increase
        real_colour = "#00C49F" if real_pct <= 0 else "#FF8800"

        st.markdown(
            f"""
            <div style='background:#1C2333; padding:1rem; border-radius:8px;
                        margin-bottom:0.75rem; border-left:3px solid #00C49F;'>
                <div style='display:flex; justify-content:space-between;
                            align-items:flex-start; flex-wrap:wrap; gap:0.5rem;'>
                    <strong style='font-size:1rem;'>
                        {category.replace('_',' ').title()}
                    </strong>
                    <span style='color:#AAAAAA; font-size:0.85rem;'>
                        {currency} {info['previous_spend']:,.0f}
                        → {currency} {info['current_spend']:,.0f}
                    </span>
                </div>
                <div style='display:flex; gap:2rem; margin-top:0.5rem; flex-wrap:wrap;'>
                    <span style='font-size:0.9rem;'>
                        Nominal: <strong style='color:#FF8800;'>{nom_pct:+.1f}%</strong>
                    </span>
                    <span style='font-size:0.9rem;'>
                        Inflation ({category.replace('_',' ').title()} CPI):
                        <strong>{inf_pct:.1f}%</strong>
                    </span>
                    <span style='font-size:0.9rem;'>
                        Real: <strong style='color:{real_colour};'>{real_pct:+.1f}%</strong>
                    </span>
                </div>
                <div style='margin-top:0.5rem; font-size:0.85rem; color:#CCCCCC;
                            font-style:italic;'>
                    {info['interpretation']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No category data available for the selected months.")

st.divider()

# ── ECONOMIC EXPLANATION ──────────────────────────────────────────────────────

with st.expander("📚 The Fisher Equation — Why Real vs Nominal Matters", expanded=False):
    st.markdown(
        f"""
        #### Nominal vs Real: The Most Important Distinction in Economics

        **The nominal value** of your spending is simply what you paid —
        the number on your bank statement.

        **The real value** adjusts for the change in the price level.
        It tells you whether you are actually consuming more or less,
        or just paying more for the same things.

        **The formula used here** is a direct application of the Fisher equation:

        > *Real change = ((1 + nominal change) / (1 + inflation rate)) − 1*

        Named after Irving Fisher (1867–1947), this equation is foundational
        in macroeconomics and appears in every discussion of monetary policy,
        interest rates, and consumer welfare.

        **A concrete example from Kenya's recent history:**
        In early 2023, Kenya's food inflation was above 10%. A household
        increasing food spending by 10% during this period had a real food
        spending change of approximately:

        > ((1 + 0.10) / (1 + 0.10)) − 1 = **0% real change**

        They were paying 10% more but consuming the same amount.
        The nominal increase was entirely an inflation effect.

        **Kenya vs Sub-Saharan Africa:**
        Kenya's current headline inflation of **{headline * 100:.1f}%** is
        significantly lower than the Sub-Saharan Africa average of
        **{ssa * 100:.1f}%**. This reflects the Central Bank of Kenya's
        relatively effective monetary policy compared to regional peers
        such as Nigeria and Ethiopia, which have experienced much higher
        inflation in recent years.

        *Source: Kenya National Bureau of Statistics (KNBS) CPI Reports;
        World Bank Global Economic Prospects.*
        """
    )

render_footer()
