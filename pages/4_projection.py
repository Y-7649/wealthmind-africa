"""
pages/4_projection.py
WealthMind Africa — Wealth Projection

Projects future net worth under four scenarios using compound growth.
An interactive savings rate slider and return rate slider let users
explore the impact of both saving more and investing more consistently.

Four scenarios:
    1. Current Behaviour       — Actual savings rate, user-selected return
    2. Savings Discipline      — +5% savings rate, same return
    3. Active Investment       — Same savings, +3% return from consistent equity
    4. Inflation-Adjusted      — Real purchasing power after Kenya CPI

Economic concepts:
    Intertemporal choice, compound interest, real vs nominal returns,
    return premium from consistent equity investment.
"""

import streamlit as st
import plotly.graph_objects as go

from core.projection import (
    get_projection_data,
    NOMINAL_RETURN_RATE,
    MIN_RETURN_RATE,
    MAX_RETURN_RATE,
    ACTIVE_RETURN_PREMIUM,
)
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
    "Four scenarios projecting your net worth over 25 years. "
    "Adjust the sliders to explore how saving more, investing more consistently, "
    "and accounting for inflation each affect long-term outcomes."
)

st.markdown(
    """
    <div style='background:rgba(255,136,0,0.06); border:1px solid rgba(255,136,0,0.25);
                border-radius:8px; padding:0.6rem 1rem; font-size:0.82rem; color:#CC8800;
                margin-bottom:0.5rem;'>
        ⚠️ <strong>All return rates are assumptions, not predictions.</strong>
        Past NSE performance does not guarantee future returns.
        These projections are educational tools for understanding compound growth,
        not financial advice.
    </div>
    """,
    unsafe_allow_html=True,
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

# ── INTERACTIVE SLIDERS ───────────────────────────────────────────────────────

actual_rate = base_data["actual_savings_rate"]

st.markdown("### Adjust the Assumptions")

slider_col1, slider_col2 = st.columns(2)

with slider_col1:
    st.caption(
        f"**Monthly Savings Rate** — your actual recorded rate is **{actual_rate:.1f}%**"
    )
    custom_rate = st.slider(
        "Savings Rate (%)",
        min_value=0,
        max_value=60,
        value=int(actual_rate),
        step=1,
        format="%d%%",
        help="Percentage of monthly income that is saved or invested.",
    )

with slider_col2:
    st.caption(
        f"**Expected Annual Return (Assumption)** — NSE conservative estimate: "
        f"**{NOMINAL_RETURN_RATE * 100:.0f}%**"
    )
    custom_return = st.slider(
        "Annual Return Rate (%)",
        min_value=int(MIN_RETURN_RATE * 100),
        max_value=int(MAX_RETURN_RATE * 100),
        value=int(NOMINAL_RETURN_RATE * 100),
        step=1,
        format="%d%%",
        help=(
            "This is an assumption about future investment returns. "
            "The default (7%) is a conservative NSE estimate. "
            "Past performance does not predict future returns."
        ),
    )

# Reload projections if either slider differs from defaults
if custom_rate != int(actual_rate) or custom_return != int(NOMINAL_RETURN_RATE * 100):
    data = get_projection_data(
        user_id,
        custom_savings_rate=float(custom_rate),
        custom_return_rate=float(custom_return),
    )
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
        delta=f"{custom_rate}% savings rate (assumption)",
        delta_color="off",
    )
with a4:
    st.metric(
        label="📊 Return Assumption",
        value=f"{custom_return}% nominal",
        delta=(
            f"{data['real_return_rate'] * 100:.1f}% real after "
            f"{data['inflation_rate'] * 100:.1f}% inflation"
        ),
        delta_color="off",
        help="Conservative NSE estimate. Real return = nominal minus inflation effect (Fisher equation).",
    )

st.divider()

# ── FOUR-SCENARIO CHART ───────────────────────────────────────────────────────

st.markdown("### 25-Year Wealth Projection (Four Scenarios)")

years         = data["years"]
current_path  = data["current_path"]
improved_path = data["improved_path"]
active_path   = data["active_path"]
real_path     = data["real_path"]

active_return_pct = data["active_return_rate"] * 100

fig = go.Figure()

# Scenario 3: Active investment (highest nominal line)
fig.add_trace(go.Scatter(
    x=years, y=active_path,
    name=f"Active Investment ({active_return_pct:.0f}% assumed return)",
    mode="lines",
    line=dict(color="#00C49F", width=2.5),
    hovertemplate=f"Year %{{x}}: {currency} %{{y:,.0f}}<extra>Active Investment</extra>",
))

# Scenario 2: Savings discipline
fig.add_trace(go.Scatter(
    x=years, y=improved_path,
    name=f"+5% Savings Rate ({custom_rate + 5}% savings)",
    mode="lines",
    line=dict(color="#7BC8A4", width=2, dash="dot"),
    hovertemplate=f"Year %{{x}}: {currency} %{{y:,.0f}}<extra>+5% Savings</extra>",
))

# Scenario 1: Current path (reference line)
fig.add_trace(go.Scatter(
    x=years, y=current_path,
    name=f"Current Behaviour ({custom_rate}% savings, {custom_return}% return)",
    mode="lines",
    line=dict(color="#FF8800", width=2.5),
    hovertemplate=f"Year %{{x}}: {currency} %{{y:,.0f}}<extra>Current Behaviour</extra>",
))

# Scenario 4: Real wealth (purchasing power)
fig.add_trace(go.Scatter(
    x=years, y=real_path,
    name=f"Real Purchasing Power ({data['real_return_rate'] * 100:.1f}% real return)",
    mode="lines",
    line=dict(color="#8888FF", width=2, dash="dot"),
    hovertemplate=f"Year %{{x}}: {currency} %{{y:,.0f}}<extra>Real Wealth</extra>",
))

fig.add_vline(x=10, line_dash="dash", line_color="#555555",
              annotation_text="Year 10", annotation_position="top")
fig.add_vline(x=25, line_dash="dash", line_color="#555555",
              annotation_text="Year 25", annotation_position="top")

fig.update_layout(
    height=440,
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
        tickprefix=f"{currency} ",
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
        font=dict(size=11),
    ),
    margin=dict(t=60, b=60, l=80, r=20),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "ℹ️ All projections assume constant monthly savings contributions and "
    f"a constant annual return of {custom_return}% (Active Investment: "
    f"{active_return_pct:.0f}%). Neither is guaranteed in practice. "
    "Projections are for educational illustration only."
)

st.divider()

# ── MILESTONE SUMMARY TABLE ───────────────────────────────────────────────────

st.markdown("### Key Milestones")

t10 = data["at_10_years"]
t25 = data["at_25_years"]

col_h, col_10, col_25 = st.columns([1.8, 1, 1])

with col_h:
    st.markdown("**Scenario**")
with col_10:
    st.markdown("**At Year 10**")
with col_25:
    st.markdown("**At Year 25**")

st.divider()

rows = [
    ("🟢 Active Investment",         t10["active"],   t25["active"],   "#00C49F"),
    ("🟡 +5% Savings Rate",          t10["improved"], t25["improved"], "#7BC8A4"),
    ("🟠 Current Behaviour",         t10["current"],  t25["current"],  "#FF8800"),
    ("🔵 Real Purchasing Power",      t10["real"],     t25["real"],     "#8888FF"),
]

for label, val_10, val_25, colour in rows:
    c1, c2, c3 = st.columns([1.8, 1, 1])
    c1.markdown(f"<span style='color:{colour};'>{label}</span>", unsafe_allow_html=True)
    c2.markdown(f"**{currency} {val_10:,.0f}**")
    c3.markdown(f"**{currency} {val_25:,.0f}**")

st.divider()

# ── WHAT THE GAPS MEAN ────────────────────────────────────────────────────────

gap_savings_25  = t25["improved"] - t25["current"]
gap_active_25   = t25["active"]   - t25["current"]
gap_inflation_25 = t25["current"] - t25["real"]

st.markdown("### What Each Scenario Gap Reveals")

g1, g2, g3 = st.columns(3)

with g1:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left:3px solid #7BC8A4;'>
            <div style='font-size:0.8rem; color:#8899AA; margin-bottom:0.3rem;'>
                SAVINGS DISCIPLINE PREMIUM
            </div>
            <div style='font-size:1.4rem; font-weight:700; color:#7BC8A4;'>
                {currency} {gap_savings_25:,.0f}
            </div>
            <div style='font-size:0.82rem; color:#8899AA; margin-top:0.4rem;'>
                Additional wealth at year 25 from saving 5% more each month.
                The cost of consumption today becomes the wealth gap at retirement.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g2:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left:3px solid #00C49F;'>
            <div style='font-size:0.8rem; color:#8899AA; margin-bottom:0.3rem;'>
                INVESTMENT CONSISTENCY PREMIUM
            </div>
            <div style='font-size:1.4rem; font-weight:700; color:#00C49F;'>
                {currency} {gap_active_25:,.0f}
            </div>
            <div style='font-size:0.82rem; color:#8899AA; margin-top:0.4rem;'>
                Additional wealth from investing consistently at {active_return_pct:.0f}%
                vs. {custom_return}%. Same savings amount — different destination.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g3:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left:3px solid #8888FF;'>
            <div style='font-size:0.8rem; color:#8899AA; margin-bottom:0.3rem;'>
                INFLATION EROSION
            </div>
            <div style='font-size:1.4rem; font-weight:700; color:#8888FF;'>
                {currency} {gap_inflation_25:,.0f}
            </div>
            <div style='font-size:0.82rem; color:#8899AA; margin-top:0.4rem;'>
                Purchasing power eroded over 25 years at Kenya's current
                {data['inflation_rate'] * 100:.1f}% inflation rate. This is
                the "inflation tax" on nominal savings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── FINANCIAL RESILIENCE ──────────────────────────────────────────────────────

st.markdown("### Financial Resilience")
st.caption(
    "How long could you maintain your current lifestyle if your income stopped today? "
    "Grounded in Deaton (1991) buffer stock saving theory."
)

r_months = data["resilience_months"]
avg_exp   = data["avg_monthly_expenses"]

if r_months >= 6:
    r_colour = "#00C49F"
    r_label  = "Strong"
    r_status = "Your balance provides strong protection against income shocks."
elif r_months >= 3:
    r_colour = "#FF8800"
    r_label  = "Adequate"
    r_status = "Within the 3–6 month recommended range. Building toward 6 months is advisable."
elif r_months >= 1:
    r_colour = "#FFCC00"
    r_label  = "Limited"
    r_status = "Below the 3-month minimum. A single income disruption risks drawing down long-term savings."
else:
    r_colour = "#FF4444"
    r_label  = "Critical"
    r_status = "Less than 1 month of coverage. Financial vulnerability is high."

res_col1, res_col2 = st.columns([1, 2])

with res_col1:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.5rem; border-radius:10px;
                    border: 2px solid {r_colour}; text-align:center;'>
            <div style='font-size:2.8rem; font-weight:800; color:{r_colour};
                        line-height:1;'>{r_months:.1f}</div>
            <div style='font-size:0.85rem; color:#AAAAAA; margin-top:0.3rem;'>months of runway</div>
            <div style='font-size:1rem; font-weight:600; color:{r_colour};
                        margin-top:0.5rem;'>{r_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with res_col2:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-left: 3px solid {r_colour};'>
            <strong>At your current expense rate of {currency} {avg_exp:,.0f}/month:</strong>
            <br><br>
            {r_status}
            <br><br>
            <div style='display:flex; gap:1.5rem; flex-wrap:wrap; font-size:0.85rem;'>
                <span>3 months (minimum): <strong style='color:#FF8800;'>
                    {currency} {avg_exp * 3:,.0f}</strong></span>
                <span>6 months (recommended): <strong style='color:#00C49F;'>
                    {currency} {avg_exp * 6:,.0f}</strong></span>
            </div>
            <br>
            <span style='color:#7A8EA0; font-size:0.8rem;'>
                Buffer stock saving theory (Deaton, 1991) demonstrates that liquid reserves
                allow households to maintain consumption through income shocks without
                resorting to costly debt or premature liquidation of long-term savings.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── ACADEMIC EXPLANATION ──────────────────────────────────────────────────────

with st.expander("📚 The Economics Behind the Four Scenarios", expanded=False):
    st.markdown(
        f"""
        #### Why Four Scenarios?

        Each scenario isolates a single economic variable, keeping everything
        else constant. This is the approach used in macroeconomic analysis to
        identify the marginal effect of one change.

        **Scenario 1 — Current Behaviour** is the baseline.
        It assumes you continue exactly as you are now: same savings rate,
        same investment return assumption.

        **Scenario 2 — Savings Discipline** holds the return rate constant
        and increases the savings rate by 5 percentage points. The gap between
        this line and the baseline isolates *the value of saving more*.
        Grounded in Friedman's Permanent Income Hypothesis (1957): the
        fraction of income saved is the primary determinant of long-run
        wealth accumulation.

        **Scenario 3 — Active Investment** holds the savings rate constant
        and increases the assumed return by {ACTIVE_RETURN_PREMIUM * 100:.0f}%
        to model the premium from consistently investing in NSE equities rather
        than holding savings in mixed or low-yield cash accounts.
        The gap isolates *the value of investing consistently*. This demonstrates
        that *where you put your savings* matters as much as *how much you save*.

        **Scenario 4 — Real Purchasing Power** applies the Fisher equation
        to the current path, adjusting for Kenya's inflation rate of
        {data['inflation_rate'] * 100:.1f}%. The gap between the nominal
        and real paths is the "inflation tax" — the silent erosion of wealth
        that occurs when inflation is not accounted for. Named after Irving Fisher
        (1867–1947), whose equation (*r_real ≈ r_nominal − π*) remains
        foundational in monetary economics.

        #### The Compound Growth Formula

        > *FV = P(1+r)ⁿ + C × [((1+r)ⁿ − 1) / r]*

        Where P is the starting balance, r is the monthly return rate,
        n is months elapsed, and C is the monthly contribution.

        **Monthly rate conversion:** This model uses *(1 + annual)^(1/12) − 1*
        rather than dividing by 12 — the compound conversion is
        mathematically correct for continuously compounding returns.

        #### Return Rate Assumption: {custom_return}%

        The current return assumption of **{custom_return}% nominal annual return**
        {"equals" if custom_return == int(NOMINAL_RETURN_RATE * 100) else "differs from"}
        the default of {NOMINAL_RETURN_RATE * 100:.0f}% — a conservative estimate
        based on the Nairobi Securities Exchange (NSE) All-Share Index historical
        average, adjusted downward from the US S&P 500 long-run average (~10%)
        to account for emerging market risk, lower liquidity, and higher
        transaction costs.

        **This assumption is not a prediction.** Use the slider to explore
        how different market environments would affect your outcomes.
        """
    )

render_footer()
