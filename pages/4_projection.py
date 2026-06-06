"""
pages/4_projection.py
WealthMind Africa — Wealth Projection

Projects future net worth under three scenarios using compound growth.
An interactive slider lets users explore the impact of changing their
savings rate on long-term wealth outcomes.

The visual gap between the three scenario lines is the most compelling
demonstration of compound interest and intertemporal choice that exists.
"""

import streamlit as st
import plotly.graph_objects as go

from core.projection import get_projection_data, NOMINAL_RETURN_RATE
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Wealth Projection — WealthMind Africa",
    page_icon="📈",
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

render_sidebar("projection")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#00C49F;'>📈 Wealth Projection</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Three scenarios projecting your net worth over 25 years. "
    "Use the slider to explore how changing your savings rate changes your outcome."
)
st.divider()

# ── LOAD BASE DATA ────────────────────────────────────────────────────────────

base_data = get_projection_data(user_id)

if not base_data.get("has_data"):
    st.info(
        "📋 **More data needed.**  \n"
        "Record at least one month of income on the **Transactions** page "
        "to generate a wealth projection."
    )
    st.page_link("pages/1_dashboard.py", label="→ Go to Transactions")
    st.stop()

# ── INTERACTIVE SAVINGS RATE SLIDER ──────────────────────────────────────────

actual_rate = base_data["actual_savings_rate"]

st.markdown("### Explore: Adjust Your Savings Rate")
st.caption(
    "Move the slider to see how a different savings rate changes your "
    "projected wealth at 10 and 25 years. Your actual recorded rate is "
    f"**{actual_rate:.1f}%**."
)

custom_rate = st.slider(
    "Monthly Savings Rate (%)",
    min_value=0,
    max_value=60,
    value=int(actual_rate),
    step=1,
    format="%d%%",
    help="Percentage of monthly income that is saved/invested",
)

# Reload projections with the custom rate if it differs from actual
if custom_rate != int(actual_rate):
    data = get_projection_data(user_id, custom_savings_rate=float(custom_rate))
else:
    data = base_data

st.divider()

# ── ASSUMPTIONS DISPLAY ───────────────────────────────────────────────────────

a1, a2, a3, a4 = st.columns(4)

with a1:
    st.metric(
        label="💰 Starting Balance",
        value=f"{currency} {data['current_balance']:,.0f}",
    )
with a2:
    st.metric(
        label="📥 Avg Monthly Income",
        value=f"{currency} {data['monthly_income']:,.0f}",
    )
with a3:
    st.metric(
        label="💾 Monthly Savings",
        value=f"{currency} {data['monthly_savings']:,.0f}",
        delta=f"{custom_rate}% savings rate",
        delta_color="off",
    )
with a4:
    st.metric(
        label="📊 Return Assumption",
        value=f"{NOMINAL_RETURN_RATE * 100:.0f}% nominal",
        delta=f"{data['real_return_rate'] * 100:.1f}% real (after {data['inflation_rate'] * 100:.1f}% inflation)",
        delta_color="off",
        help="Conservative NSE historical average. Real return = nominal minus inflation effect.",
    )

st.divider()

# ── THREE-SCENARIO CHART ──────────────────────────────────────────────────────

st.markdown("### 25-Year Wealth Projection")

years          = data["years"]
current_path   = data["current_path"]
improved_path  = data["improved_path"]
real_path      = data["real_path"]

fig = go.Figure()

# Scenario 2: Improved (top line — aspirational)
fig.add_trace(go.Scatter(
    x=years, y=improved_path,
    name=f"Improved (+5% savings rate = {custom_rate + 5}%)",
    mode="lines",
    line=dict(color="#00C49F", width=2.5),
))

# Scenario 1: Current path (middle line)
fig.add_trace(go.Scatter(
    x=years, y=current_path,
    name=f"Current path ({custom_rate}% savings rate)",
    mode="lines",
    line=dict(color="#FF8800", width=2.5),
))

# Scenario 3: Real returns (bottom line — most conservative)
fig.add_trace(go.Scatter(
    x=years, y=real_path,
    name=f"Inflation-adjusted ({data['real_return_rate'] * 100:.1f}% real return)",
    mode="lines",
    line=dict(color="#8888FF", width=2, dash="dot"),
))

# Mark year 10 and year 25 with vertical reference lines
fig.add_vline(x=10, line_dash="dash", line_color="#555555",
              annotation_text="Year 10", annotation_position="top")
fig.add_vline(x=25, line_dash="dash", line_color="#555555",
              annotation_text="Year 25", annotation_position="top")

fig.update_layout(
    height=420,
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#FAFAFA"),
    xaxis=dict(
        title="Years from today",
        showgrid=False,
        color="#AAAAAA",
        dtick=5,
    ),
    yaxis=dict(
        title=f"Projected Net Worth ({currency})",
        showgrid=True,
        gridcolor="#2A2A3A",
        color="#AAAAAA",
        tickprefix="KES ",
        tickformat=",.0f",
    ),
    legend=dict(
        bgcolor="#1C2333",
        bordercolor="#2A2A3A",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    margin=dict(t=60, b=60, l=80, r=20),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── MILESTONE SUMMARY TABLE ───────────────────────────────────────────────────

st.markdown("### Key Milestones")

t10 = data["at_10_years"]
t25 = data["at_25_years"]

# Gap between improved and current — the value of saving 5% more
gap_10 = t10["improved"] - t10["current"]
gap_25 = t25["improved"] - t25["current"]

col_h, col_10, col_25 = st.columns([1.5, 1, 1])

with col_h:
    st.markdown("**Scenario**")
with col_10:
    st.markdown("**At Year 10**")
with col_25:
    st.markdown("**At Year 25**")

st.divider()

rows = [
    (f"Current path ({custom_rate}% savings)",    t10["current"],  t25["current"],  "#FF8800"),
    (f"Improved (+5% = {custom_rate+5}% savings)", t10["improved"], t25["improved"], "#00C49F"),
    (f"Inflation-adjusted ({data['real_return_rate']*100:.1f}% real)", t10["real"], t25["real"], "#8888FF"),
]

for label, val_10, val_25, colour in rows:
    c1, c2, c3 = st.columns([1.5, 1, 1])
    c1.markdown(f"<span style='color:{colour};'>●</span> {label}", unsafe_allow_html=True)
    c2.markdown(f"**{currency} {val_10:,.0f}**")
    c3.markdown(f"**{currency} {val_25:,.0f}**")

st.divider()

# Highlight the compound effect
st.markdown(
    f"""
    <div style='background:#1C2333; padding:1rem; border-radius:8px;
                border-left:3px solid #00C49F;'>
        <strong>The Compound Effect</strong><br><br>
        Saving an extra 5% of income per month means an additional
        <strong style='color:#00C49F;'>{currency} {gap_10:,.0f}</strong> at year 10
        and <strong style='color:#00C49F;'>{currency} {gap_25:,.0f}</strong> at year 25.<br><br>
        <span style='color:#AAAAAA; font-size:0.9rem;'>
        The gap grows non-linearly because each additional month of savings
        compounds on all previous savings. This is what economists mean
        when they describe the power of compound interest.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── ECONOMIC EXPLANATION ──────────────────────────────────────────────────────

with st.expander("📚 Compound Interest & Intertemporal Choice", expanded=False):
    st.markdown(
        f"""
        #### Why the Lines Diverge So Dramatically

        **Compound interest** means that returns are earned not just on the
        original savings, but on all previously accumulated returns. This
        creates exponential growth — which is why the lines in the chart
        above accelerate upward rather than growing linearly.

        The formula used:
        > *FV = P(1+r)ⁿ + C × [((1+r)ⁿ − 1) / r]*

        Where P is the current balance, r is the monthly return rate,
        n is months elapsed, and C is the monthly contribution.

        **Intertemporal choice** is the economic study of how decisions
        made today have consequences across time. The savings rate slider
        above is a direct tool for intertemporal analysis: you are choosing
        how much current consumption to sacrifice for future wealth.

        **The return assumption:**
        This projection uses **{NOMINAL_RETURN_RATE * 100:.0f}% nominal annual return** —
        a conservative estimate based on the Nairobi Securities Exchange (NSE)
        All-Share Index historical performance. This is below the long-run
        US S&P 500 average (~10%) to account for emerging market risk.

        After accounting for Kenya's current inflation of
        **{data['inflation_rate'] * 100:.1f}%**, the real return is approximately
        **{data['real_return_rate'] * 100:.1f}%** — shown as the dotted blue line.
        The difference between the nominal and real paths is the wealth silently
        eroded by inflation over 25 years.

        **Why economists care about savings rates:**
        At the macroeconomic level, national savings rates directly determine
        investment capacity and long-run growth (Solow, 1956). The same
        mechanism operates at the individual level — your personal savings
        rate determines your long-run wealth accumulation capacity.
        """
    )

render_footer()
