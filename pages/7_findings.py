"""
pages/7_findings.py
WealthMind Africa — Economic Findings

PUBLIC page. No login required.

Presents WealthMind Africa as an economics investigation platform, not
a finance tracker. Shows what the platform discovers — using demonstration
data clearly labeled as such — in a Financial Times / research briefing style.

Sections:
    1. Inflation Findings   — nominal vs real spending adjustments
    2. Behavioural Findings — present bias patterns
    3. Savings Findings     — compound growth implications
    4. Resilience Findings  — financial runway analysis

Created by Yash Karia
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

from utils.styles import inject_global_styles
from utils.footer import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Findings — WealthMind Africa",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_styles()

# ── EXTRA CSS ─────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Research report header */
    .fin-report-kicker {
        font-size: 0.65rem;
        font-weight: 700;
        color: #00C49F;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin-bottom: 0.6rem;
    }
    .fin-report-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #E2E8F0;
        letter-spacing: -0.035em;
        line-height: 1.15;
        margin-bottom: 0.55rem;
    }
    .fin-report-deck {
        font-size: 1.05rem;
        color: #8899AA;
        line-height: 1.65;
        max-width: 680px;
        margin-bottom: 0.8rem;
    }
    .fin-byline {
        font-size: 0.75rem;
        color: #3A4A58;
        border-top: 1px solid #1A2030;
        padding-top: 0.65rem;
        margin-top: 0.65rem;
    }

    /* Demo data badge */
    .demo-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(255,136,0,0.08);
        border: 1px solid rgba(255,136,0,0.25);
        border-radius: 5px;
        padding: 0.2rem 0.6rem;
        font-size: 0.63rem;
        font-weight: 700;
        color: #CC8800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Finding section */
    .finding-number {
        font-size: 0.65rem;
        font-weight: 700;
        color: #00C49F;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin-bottom: 0.3rem;
    }
    .finding-headline {
        font-size: 1.4rem;
        font-weight: 800;
        color: #E2E8F0;
        letter-spacing: -0.025em;
        line-height: 1.25;
        margin-bottom: 0.6rem;
    }
    .finding-standfirst {
        font-size: 0.9rem;
        color: #8899AA;
        line-height: 1.65;
        margin-bottom: 1rem;
        max-width: 600px;
    }

    /* Key stat block */
    .finding-stat-row {
        display: flex;
        gap: 1rem;
        margin: 1.2rem 0;
        flex-wrap: wrap;
    }
    .finding-stat-card {
        background: linear-gradient(145deg, #0F1824, #0A1018);
        border: 1px solid #1E2738;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        min-width: 140px;
        flex: 1;
    }
    .finding-stat-label {
        font-size: 0.62rem;
        font-weight: 700;
        color: #3A5060;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.35rem;
    }
    .finding-stat-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #00C49F;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .finding-stat-sub {
        font-size: 0.68rem;
        color: #445566;
        margin-top: 0.25rem;
    }

    /* Concept tag */
    .concept-tag {
        display: inline-block;
        font-size: 0.63rem;
        background: rgba(0,196,159,0.07);
        border: 1px solid rgba(0,196,159,0.2);
        border-radius: 4px;
        padding: 0.15rem 0.5rem;
        color: #00C49F;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    /* Methodology callout */
    .methodology-box {
        background: rgba(0,0,0,0.3);
        border-left: 2px solid rgba(0,196,159,0.3);
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 0.8rem 0;
    }
    .methodology-box .meth-label {
        font-size: 0.62rem;
        font-weight: 700;
        color: #3A5060;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }
    .methodology-box .meth-text {
        font-size: 0.82rem;
        color: #7A9AB0;
        line-height: 1.55;
    }

    /* Summary box */
    .exec-summary {
        background: linear-gradient(145deg, #0F1824, #0A1018);
        border: 1px solid rgba(0,196,159,0.15);
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin: 1.4rem 0 2rem;
        position: relative;
        overflow: hidden;
    }
    .exec-summary::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00C49F, transparent);
    }
    .exec-summary-title {
        font-size: 0.65rem;
        font-weight: 700;
        color: #00C49F;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.9rem;
    }
    .exec-finding {
        display: flex;
        gap: 0.8rem;
        align-items: flex-start;
        margin-bottom: 0.65rem;
    }
    .exec-finding-num {
        font-size: 0.65rem;
        font-weight: 700;
        color: #00C49F;
        min-width: 18px;
        margin-top: 0.1rem;
    }
    .exec-finding-text {
        font-size: 0.85rem;
        color: #CCDDE8;
        line-height: 1.5;
    }

    /* Section divider */
    .section-rule {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2.8rem 0 2rem;
    }
    .section-rule-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(0,196,159,0.25), transparent);
    }
    .section-rule-label {
        font-size: 0.62rem;
        font-weight: 700;
        color: #00C49F;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        white-space: nowrap;
    }

    @media (max-width: 768px) {
        .fin-report-title { font-size: 1.7rem; }
        .finding-headline { font-size: 1.15rem; }
        .finding-stat-row { flex-direction: column; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── REPORT HEADER ─────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="fin-report-kicker">WealthMind Africa &nbsp;·&nbsp; Economics Research</div>
    <div class="fin-report-title">What the data reveals about financial behaviour in Kenya</div>
    <div class="fin-report-deck">
        WealthMind Africa is an economics investigation platform, not a budgeting app.
        It applies concepts from macroeconomics and behavioural finance to personal
        transaction data — finding signals that simple expense trackers miss entirely.
        The findings below are drawn from demonstration data, clearly labeled.
        Create an account to generate findings from your own financial behaviour.
    </div>
    <div class="fin-byline">
        By <strong style="color:#556677;">Yash Karia</strong>
        &nbsp;·&nbsp; Applied Economics Platform
        &nbsp;·&nbsp; <a href="mailto:yashkaria.pro@gmail.com"
                        style="color:#3A5060; text-decoration:none;">
                        yashkaria.pro@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="exec-summary">
        <div class="exec-summary-title">Key Findings — Demonstration Data</div>
        <div class="exec-finding">
            <span class="exec-finding-num">01</span>
            <span class="exec-finding-text">
                Food spending increased 12% in nominal terms — but only 4% in real terms
                once adjusted for Kenya's consumer price inflation. The nominal increase
                was almost entirely an inflation effect, not genuine consumption growth.
            </span>
        </div>
        <div class="exec-finding">
            <span class="exec-finding-num">02</span>
            <span class="exec-finding-text">
                Discretionary spending in the first week of the month was 38% higher than
                in the final week — a textbook signature of hyperbolic discounting, the
                behavioural bias Laibson (1997) formally modelled as present bias.
            </span>
        </div>
        <div class="exec-finding">
            <span class="exec-finding-num">03</span>
            <span class="exec-finding-text">
                A 5 percentage point increase in the monthly savings rate would add
                approximately KES 4.1 million to projected net worth over 25 years at a
                7% assumed annual return — a non-linear wealth effect from a modest
                change in current behaviour.
            </span>
        </div>
        <div class="exec-finding">
            <span class="exec-finding-num">04</span>
            <span class="exec-finding-text">
                Reducing monthly expenses by 20% increased financial runway from 2.4 months
                to 3.8 months — a 58% improvement in resilience from a single behavioural
                adjustment, not increased income.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# FINDING 1 — INFLATION
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="section-rule">
        <span class="section-rule-label">Finding 01 — Inflation</span>
        <div class="section-rule-line"></div>
        <span class="demo-badge">⚠ Demonstration data</span>
    </div>
    <div class="finding-number">Finding 01 of 04</div>
    <div class="finding-headline">
        Inflation explains most of the apparent increase in food spending —
        real consumption barely changed
    </div>
    <div class="finding-standfirst">
        A 12% rise in food spending looked alarming. After applying the Fisher equation
        with Kenya's category-specific food CPI, the real increase was only 4%.
        The other 8 percentage points were inflation — not more food consumed.
    </div>
    """,
    unsafe_allow_html=True,
)

# Key stats
st.markdown(
    """
    <div class="finding-stat-row">
        <div class="finding-stat-card">
            <div class="finding-stat-label">Nominal Change</div>
            <div class="finding-stat-value" style="color:#FF8800;">+12.0%</div>
            <div class="finding-stat-sub">What the bank statement showed</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Real Change</div>
            <div class="finding-stat-value" style="color:#00C49F;">+4.1%</div>
            <div class="finding-stat-sub">Actual consumption growth</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Inflation Effect</div>
            <div class="finding-stat-value" style="color:#8888FF;">7.9pp</div>
            <div class="finding-stat-sub">Pure price level effect</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Kenya Food CPI</div>
            <div class="finding-stat-value" style="color:#8899AA;">7.9%</div>
            <div class="finding-stat-sub">KNBS category estimate</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chart: Nominal vs Real spending comparison bar
_categories = ["Food", "Transport", "Entertainment", "Utilities"]
_nominal     = [12.0, 8.5, 6.0, 4.5]
_real        = [4.1, 2.2, 3.8, 2.0]

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    name="Nominal change (%)",
    x=_categories,
    y=_nominal,
    marker_color="#FF8800",
    marker_line_width=0,
    hovertemplate="%{x}: +%{y:.1f}% nominal<extra></extra>",
))
fig1.add_trace(go.Bar(
    name="Real change after Kenya CPI (%)",
    x=_categories,
    y=_real,
    marker_color="#00C49F",
    marker_line_width=0,
    hovertemplate="%{x}: +%{y:.1f}% real<extra></extra>",
))
fig1.update_layout(
    barmode="group",
    height=260,
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#8899AA", size=11),
    xaxis=dict(showgrid=False, color="#4A6070"),
    yaxis=dict(
        showgrid=True, gridcolor="#1A2030", color="#4A6070",
        ticksuffix="%", title="Spending change (%)",
    ),
    legend=dict(bgcolor="#0E1117", font=dict(size=10)),
    margin=dict(t=10, b=40, l=55, r=20),
    bargap=0.25,
    bargroupgap=0.08,
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    """
    <div class="methodology-box">
        <div class="meth-label">Methodology</div>
        <div class="meth-text">
            Real spending change is computed using the Fisher equation:
            <em>real change = ((1 + nominal) / (1 + inflation)) − 1</em>,
            where inflation is drawn from Kenya National Bureau of Statistics (KNBS)
            category-specific CPI data. Food inflation and transport inflation use
            category-weighted rates rather than the headline CPI, giving a more
            accurate picture of each spending category's real change.
        </div>
    </div>
    <span class="concept-tag">Fisher Equation</span>
    <span class="concept-tag">Real vs Nominal</span>
    <span class="concept-tag">KNBS CPI</span>
    <span class="concept-tag">Consumption Analysis</span>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/3_inflation.py", label="→ Open Kenya Inflation Context module")

# ─────────────────────────────────────────────────────────────────────────────
# FINDING 2 — PRESENT BIAS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="section-rule">
        <span class="section-rule-label">Finding 02 — Behavioural Economics</span>
        <div class="section-rule-line"></div>
        <span class="demo-badge">⚠ Demonstration data</span>
    </div>
    <div class="finding-number">Finding 02 of 04</div>
    <div class="finding-headline">
        Spending is 38% higher in the first week of the month —
        a textbook signature of present bias
    </div>
    <div class="finding-standfirst">
        Laibson's hyperbolic discounting model predicts that people over-weight
        immediate consumption relative to future welfare. This shows up in
        spending data: money is disproportionately spent immediately after income
        arrives, with discretionary spending falling sharply by week four.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="finding-stat-row">
        <div class="finding-stat-card">
            <div class="finding-stat-label">Present Bias Index</div>
            <div class="finding-stat-value" style="color:#FF8800;">1.38</div>
            <div class="finding-stat-sub">Week 1 / Week 4 ratio</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Week 1 Spending</div>
            <div class="finding-stat-value">KES 9,820</div>
            <div class="finding-stat-sub">Avg discretionary</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Week 4 Spending</div>
            <div class="finding-stat-value" style="color:#8899AA;">KES 7,115</div>
            <div class="finding-stat-sub">Avg discretionary</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Monthly Bias Cost</div>
            <div class="finding-stat-value" style="color:#FF8800;">KES 1,450</div>
            <div class="finding-stat-sub">Est. excess spend</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chart: Weekly spending bar
_weeks         = ["Week 1", "Week 2", "Week 3", "Week 4"]
_demo_spending = [9820, 8650, 7840, 7115]
_rational_ref  = [8356, 8356, 8356, 8356]  # equal smoothed spending

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    name="Actual weekly discretionary spending",
    x=_weeks,
    y=_demo_spending,
    marker_color=["#FF8800", "#CC7700", "#AA6600", "#886600"],
    marker_line_width=0,
    hovertemplate="%{x}: KES %{y:,.0f}<extra></extra>",
))
fig2.add_trace(go.Scatter(
    name="Smoothed (rational) baseline",
    x=_weeks,
    y=_rational_ref,
    mode="lines",
    line=dict(color="#00C49F", width=2, dash="dash"),
    hovertemplate="Rational baseline: KES %{y:,.0f}<extra></extra>",
))
fig2.update_layout(
    height=260,
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#8899AA", size=11),
    xaxis=dict(showgrid=False, color="#4A6070"),
    yaxis=dict(
        showgrid=True, gridcolor="#1A2030", color="#4A6070",
        tickprefix="KES ", tickformat=",.0f",
        title="Avg weekly spending",
    ),
    legend=dict(bgcolor="#0E1117", font=dict(size=10)),
    margin=dict(t=10, b=40, l=80, r=20),
    bargap=0.3,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    """
    <div class="methodology-box">
        <div class="meth-label">Methodology</div>
        <div class="meth-text">
            The Present Bias Index is computed as Week 1 discretionary spending ÷ Week 4
            discretionary spending, averaged across recorded months. An index above 1.0
            indicates present bias — spending front-loaded toward the immediate post-income
            period. The <em>rational baseline</em> represents what perfectly smoothed
            consumption would look like: equal spending in each week, consistent with
            Hall's (1978) consumption smoothing theory. The gap between actual and
            baseline isolates the behavioural component.
        </div>
    </div>
    <span class="concept-tag">Laibson (1997)</span>
    <span class="concept-tag">Hyperbolic Discounting</span>
    <span class="concept-tag">Consumption Smoothing</span>
    <span class="concept-tag">Hall (1978)</span>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/5_behaviour.py", label="→ Open Present Bias Detection module")

# ─────────────────────────────────────────────────────────────────────────────
# FINDING 3 — SAVINGS & COMPOUND GROWTH
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="section-rule">
        <span class="section-rule-label">Finding 03 — Long-Term Wealth</span>
        <div class="section-rule-line"></div>
        <span class="demo-badge">⚠ Demonstration data</span>
    </div>
    <div class="finding-number">Finding 03 of 04</div>
    <div class="finding-headline">
        A 5% increase in savings rate produces a disproportionately large
        wealth effect — compound growth amplifies small changes dramatically
    </div>
    <div class="finding-standfirst">
        At a 12% savings rate, the 25-year projected net worth is KES 11.2 million.
        Increasing the rate to 17% — still a modest change — produces KES 15.3 million.
        The KES 4.1 million gap is not a 40% improvement in savings: it is the
        non-linear power of compound growth.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="finding-stat-row">
        <div class="finding-stat-card">
            <div class="finding-stat-label">Current Savings Rate</div>
            <div class="finding-stat-value" style="color:#FF8800;">12%</div>
            <div class="finding-stat-sub">Monthly income saved</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">25-Year Projection</div>
            <div class="finding-stat-value">KES 11.2M</div>
            <div class="finding-stat-sub">Current behaviour</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">At 17% Savings Rate</div>
            <div class="finding-stat-value" style="color:#00C49F;">KES 15.3M</div>
            <div class="finding-stat-sub">+5pp savings discipline</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Compound Premium</div>
            <div class="finding-stat-value" style="color:#00C49F;">KES 4.1M</div>
            <div class="finding-stat-sub">Additional wealth at year 25</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chart: Compound growth curves

def _compound_path(monthly_income, savings_pct, annual_return, years=25):
    """Generate simplified compound growth path for demo chart."""
    monthly_rate = (1 + annual_return) ** (1/12) - 1
    monthly_saving = monthly_income * savings_pct / 100
    balance = 0
    path = []
    for y in range(years + 1):
        path.append(balance)
        for _ in range(12):
            balance = balance * (1 + monthly_rate) + monthly_saving
    return path

_demo_income = 80000  # KES monthly
_years_x     = list(range(26))
_path_current  = _compound_path(_demo_income, 12, 0.07)
_path_improved = _compound_path(_demo_income, 17, 0.07)
_path_active   = _compound_path(_demo_income, 12, 0.10)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=_years_x, y=_path_active,
    name="Active investment (10% assumed return)",
    mode="lines",
    line=dict(color="#00C49F", width=2.5),
    hovertemplate="Year %{x}: KES %{y:,.0f}<extra>Active</extra>",
))
fig3.add_trace(go.Scatter(
    x=_years_x, y=_path_improved,
    name="Savings discipline (17% savings rate)",
    mode="lines",
    line=dict(color="#7BC8A4", width=2, dash="dot"),
    hovertemplate="Year %{x}: KES %{y:,.0f}<extra>17% savings</extra>",
))
fig3.add_trace(go.Scatter(
    x=_years_x, y=_path_current,
    name="Current behaviour (12% savings, 7% return)",
    mode="lines",
    line=dict(color="#FF8800", width=2.5),
    hovertemplate="Year %{x}: KES %{y:,.0f}<extra>Current</extra>",
))
fig3.add_vline(x=10, line_dash="dash", line_color="#2A3A48",
               annotation_text="Year 10", annotation_font_color="#4A6070")
fig3.add_vline(x=25, line_dash="dash", line_color="#2A3A48",
               annotation_text="Year 25", annotation_font_color="#4A6070")
fig3.update_layout(
    height=280,
    paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
    font=dict(color="#8899AA", size=11),
    xaxis=dict(showgrid=False, color="#4A6070", title="Years from today", dtick=5),
    yaxis=dict(
        showgrid=True, gridcolor="#1A2030", color="#4A6070",
        tickprefix="KES ", tickformat=",.0f",
        title="Projected net worth",
    ),
    legend=dict(bgcolor="#0E1117", font=dict(size=10),
                orientation="h", y=1.03, x=0),
    margin=dict(t=40, b=50, l=90, r=20),
    hovermode="x unified",
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    """
    <div class="methodology-box">
        <div class="meth-label">Methodology</div>
        <div class="meth-text">
            Projections use the compound growth formula
            <em>FV = P(1+r)ⁿ + C × [((1+r)ⁿ − 1) / r]</em>,
            with monthly rate conversion <em>(1 + annual)^(1/12) − 1</em>.
            Return rate of 7% is a conservative NSE-calibrated assumption.
            All projections are educational illustrations, not financial advice.
            The 7% default reflects the NSE All-Share Index historical average
            adjusted downward for emerging market risk premium.
        </div>
    </div>
    <span class="concept-tag">Compound Growth</span>
    <span class="concept-tag">Friedman (1957)</span>
    <span class="concept-tag">Solow Growth Model</span>
    <span class="concept-tag">Fisher (1930)</span>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/4_projection.py", label="→ Open Wealth Projection module")

# ─────────────────────────────────────────────────────────────────────────────
# FINDING 4 — FINANCIAL RESILIENCE
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="section-rule">
        <span class="section-rule-label">Finding 04 — Financial Resilience</span>
        <div class="section-rule-line"></div>
        <span class="demo-badge">⚠ Demonstration data</span>
    </div>
    <div class="finding-number">Finding 04 of 04</div>
    <div class="finding-headline">
        A 20% reduction in monthly expenses increased financial runway
        by 58% — without any change in income
    </div>
    <div class="finding-standfirst">
        Deaton's (1991) buffer stock saving theory argues that liquid reserves
        are primarily protection against income shocks, not a wealth strategy.
        Even a modest expense reduction — cutting discretionary spending by 20% —
        extends financial runway from 2.4 months to 3.8 months, moving from
        "Critical" to the lower bound of the recommended 3–6 month range.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="finding-stat-row">
        <div class="finding-stat-card">
            <div class="finding-stat-label">Current Runway</div>
            <div class="finding-stat-value" style="color:#FF8800;">2.4 mo</div>
            <div class="finding-stat-sub">At current expenses</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">After 20% Expense Cut</div>
            <div class="finding-stat-value" style="color:#00C49F;">3.8 mo</div>
            <div class="finding-stat-sub">Same balance, lower burn</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">Improvement</div>
            <div class="finding-stat-value" style="color:#00C49F;">+58%</div>
            <div class="finding-stat-sub">Resilience gain</div>
        </div>
        <div class="finding-stat-card">
            <div class="finding-stat-label">CBK Recommended</div>
            <div class="finding-stat-value" style="color:#4499FF;">3–6 mo</div>
            <div class="finding-stat-sub">Emergency buffer target</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Horizontal bar chart showing resilience scenarios
_scenarios  = ["Current (KES 45,000/mo)", "−10% Expenses", "−20% Expenses", "−30% Expenses"]
_runways    = [2.4, 2.7, 3.8, 4.9]
_bar_colors = ["#FF8800", "#FFAA33", "#00C49F", "#00E5B8"]

fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=_runways,
    y=_scenarios,
    orientation="h",
    marker_color=_bar_colors,
    marker_line_width=0,
    text=[f"{v:.1f} months" for v in _runways],
    textposition="outside",
    textfont=dict(size=11, color=_bar_colors),
    hovertemplate="%{y}: %{x:.1f} months runway<extra></extra>",
    width=0.5,
))
fig4.add_vline(x=3.0, line_dash="dash", line_color="#4A6070",
               annotation_text="3-month minimum",
               annotation_font_color="#4A6070",
               annotation_position="top")
fig4.add_vline(x=6.0, line_dash="dash", line_color="#00C49F",
               annotation_text="6-month target",
               annotation_font_color="#00C49F",
               annotation_position="top")
fig4.update_layout(
    height=220,
    paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
    font=dict(color="#8899AA", size=11),
    xaxis=dict(
        showgrid=True, gridcolor="#1A2030", color="#4A6070",
        title="Financial runway (months)", range=[0, 8],
    ),
    yaxis=dict(showgrid=False, color="#7A9AB0"),
    margin=dict(t=30, b=50, l=180, r=80),
    bargap=0.4,
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    """
    <div class="methodology-box">
        <div class="meth-label">Methodology</div>
        <div class="meth-text">
            Financial runway = current balance ÷ average monthly expenses.
            The scenario analysis holds the balance constant and reduces
            monthly expenses by 10%, 20%, and 30% to isolate the impact of
            expense reduction on buffer stock adequacy. This demonstrates that
            resilience is a function of both accumulated assets <em>and</em>
            consumption rate — an insight from Deaton (1991) that most
            personal finance tools ignore entirely.
        </div>
    </div>
    <span class="concept-tag">Deaton (1991)</span>
    <span class="concept-tag">Buffer Stock Saving</span>
    <span class="concept-tag">Financial Resilience</span>
    <span class="concept-tag">CBK FinAccess</span>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/4_projection.py", label="→ Open Wealth Projection module")

# ── CTA ───────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="section-rule">
        <span class="section-rule-label">Generate Your Own Findings</span>
        <div class="section-rule-line"></div>
    </div>
    <div style="background:linear-gradient(145deg,#0F1824,#0A1018);
                border:1px solid rgba(0,196,159,0.2); border-radius:14px;
                padding:2rem 2.2rem; max-width:600px; margin-bottom:1.5rem;">
        <div style="font-size:1.1rem; font-weight:700; color:#E2E8F0; margin-bottom:0.55rem;">
            The findings above used demonstration data.
        </div>
        <div style="font-size:0.85rem; color:#8899AA; line-height:1.65; margin-bottom:1.2rem;">
            Create a free account and start recording your own income and expenses.
            WealthMind Africa will generate these same analyses — inflation adjustment,
            present bias detection, compound growth projection, resilience scoring —
            using your real financial data.
        </div>
        <div style="font-size:0.75rem; color:#3A4A58;">Free · No card required · Built for Kenya</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.page_link("app.py", label="→ Create an account or sign in")

# ── ACADEMIC FOUNDATION ───────────────────────────────────────────────────────

with st.expander("📚 Academic Foundation", expanded=False):
    st.markdown(
        """
        The four findings above are grounded in the following literature:

        - **Fisher, I. (1930).** *The Theory of Interest.* Macmillan. — Real vs nominal framework.
        - **Friedman, M. (1957).** *A Theory of the Consumption Function.* Princeton. — Savings rate and permanent income.
        - **Hall, R.E. (1978).** Stochastic Implications of the Life Cycle Hypothesis. *JPE, 86*(6). — Consumption smoothing as the rational baseline.
        - **Deaton, A. (1991).** Saving and Liquidity Constraints. *Econometrica, 59*(5). — Buffer stock saving theory.
        - **Laibson, D. (1997).** Golden Eggs and Hyperbolic Discounting. *QJE, 112*(2). — Present bias model.
        - **O'Donoghue, T. & Rabin, M. (1999).** Doing It Now or Later. *AER, 89*(1). — Commitment mechanisms.
        - **Kenya National Bureau of Statistics.** *CPI Monthly Reports.* — Category-specific inflation rates.
        - **Central Bank of Kenya. (2021).** *FinAccess Household Survey.* — 3–6 month buffer stock recommendation.
        """
    )

render_footer()
