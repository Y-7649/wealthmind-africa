"""
pages/5_behaviour.py
WealthMind Africa — Present Bias Detection

Detects hyperbolic discounting in the user's own spending data by
comparing first-week vs last-week discretionary spending patterns.

Academic foundation:
    Laibson (1997), O'Donoghue & Rabin (1999), Kahneman & Tversky (1979)
"""

import streamlit as st
import plotly.graph_objects as go

from core.present_bias import calculate_present_bias
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Present Bias — WealthMind Africa",
    page_icon="🧠",
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

render_sidebar("behaviour")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────

result = calculate_present_bias(user_id, currency=currency)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#00C49F;'>🧠 Present Bias Detection</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Statistical analysis of your spending patterns to detect "
    "**hyperbolic discounting** — a behavioural economics concept "
    "describing the tendency to over-spend immediately after receiving income."
)
st.divider()

# ── NO DATA STATE ─────────────────────────────────────────────────────────────

if not result.get("has_data"):
    st.info(
        "📋 **No spending data yet.**  \n"
        "Record discretionary expenses (food, transport, entertainment) "
        "across the month on the **Transactions** page to generate "
        "a present bias analysis."
    )
    st.page_link("pages/1_dashboard.py", label="→ Go to Transactions")
    st.stop()

# ── DATA SUFFICIENCY WARNING ──────────────────────────────────────────────────

if not result["has_sufficient_data"]:
    st.warning(
        f"⚠️ **Limited data — results are preliminary.**  \n"
        f"Only **{result['months_analysed']} month** of data is available. "
        f"At least 2 months are needed for a statistically meaningful result. "
        f"Continue recording transactions and return next month for a more "
        f"reliable reading."
    )

# ── BIAS INDEX DISPLAY ────────────────────────────────────────────────────────

idx    = result["bias_index"]
label  = result["bias_label"]
colour = result["bias_colour"]
cost   = result["implied_monthly_bias_cost"]

_, index_col, _ = st.columns([1, 2, 1])

with index_col:
    st.markdown(
        f"""
        <div style='text-align:center; background:#1C2333; padding:2rem;
                    border-radius:12px; border: 2px solid {colour};'>
            <div style='font-size:4rem; font-weight:bold;
                        color:{colour};'>{idx:.2f}</div>
            <div style='font-size:1.1rem; color:#FAFAFA;
                        margin:0.5rem 0;'>Present Bias Index</div>
            <div style='font-size:1.3rem; font-weight:bold;
                        color:{colour};'>{label}</div>
            <div style='font-size:0.85rem; color:#AAAAAA; margin-top:0.5rem;'>
                Based on {result['months_analysed']} month(s) of data
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── WEEKLY SPENDING BAR CHART ─────────────────────────────────────────────────

st.markdown("### Average Discretionary Spending by Week")
st.caption(
    "Discretionary categories: food, transport, entertainment, other expenses. "
    "Fixed obligations (rent, utilities, education, health) are excluded — "
    "they do not reflect discretionary present-biased behaviour."
)

avgs = result["weekly_averages"]
week_labels  = ["Week 1\n(Days 1–7)", "Week 2\n(Days 8–14)",
                "Week 3\n(Days 15–21)", "Week 4\n(Days 22–end)"]
week_values  = [avgs["week_1"], avgs["week_2"], avgs["week_3"], avgs["week_4"]]

# Colour Week 1 with bias colour; rest are neutral
bar_colours  = [colour, "#3A4A5A", "#3A4A5A", "#3A4A5A"]

# Add a reference line for what uniform spending would look like
avg_total   = sum(week_values)
uniform_val = avg_total / 4 if avg_total > 0 else 0

fig = go.Figure()

fig.add_trace(go.Bar(
    x=week_labels,
    y=week_values,
    marker_color=bar_colours,
    text=[f"{currency} {v:,.0f}" for v in week_values],
    textposition="outside",
    textfont=dict(color="#FAFAFA"),
    name="Avg Spending",
))

# Uniform baseline reference line
fig.add_hline(
    y=uniform_val,
    line_dash="dash",
    line_color="#AAAAAA",
    annotation_text=f"Uniform baseline: {currency} {uniform_val:,.0f}",
    annotation_position="right",
    annotation_font_color="#AAAAAA",
)

fig.update_layout(
    height=360,
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#FAFAFA"),
    xaxis=dict(showgrid=False, color="#AAAAAA"),
    yaxis=dict(
        showgrid=True,
        gridcolor="#2A2A3A",
        color="#AAAAAA",
        tickprefix=f"{currency} ",
        tickformat=",.0f",
    ),
    showlegend=False,
    margin=dict(t=40, b=60, l=80, r=120),
)

st.plotly_chart(fig, use_container_width=True)

# ── INTERPRETATION ────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div style='background:#1C2333; padding:1rem; border-radius:8px;
                border-left:3px solid {colour};'>
        <strong>Interpretation</strong><br><br>
        {result['interpretation']}
    </div>
    """,
    unsafe_allow_html=True,
)

if cost > 0:
    st.markdown(
        f"""
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left:3px solid #FF8800; margin-top:0.75rem;'>
            <strong>💸 Estimated Monthly Cost of Present Bias</strong><br><br>
            If your Week 1 spending were equal to your monthly average week,
            you would save approximately
            <strong style='color:#FF8800;'>{currency} {cost:,.0f}</strong> per month —
            <strong style='color:#FF8800;'>{currency} {cost * 12:,.0f}</strong> per year.<br><br>
            <span style='color:#AAAAAA; font-size:0.85rem;'>
            This is the "cost of impatience" — the gap between your actual
            spending behaviour and time-consistent spending.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── MONTHLY BREAKDOWN TABLE ───────────────────────────────────────────────────

if len(result["monthly_breakdown"]) > 1:
    st.markdown("### Monthly Breakdown")
    st.caption("Weekly spending for each month analysed.")

    h0, h1, h2, h3, h4, h5 = st.columns([1.2, 1, 1, 1, 1, 1])
    h0.markdown("**Month**")
    h1.markdown("**Week 1**")
    h2.markdown("**Week 2**")
    h3.markdown("**Week 3**")
    h4.markdown("**Week 4**")
    h5.markdown("**Total**")
    st.divider()

    for m in result["monthly_breakdown"]:
        c0, c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1, 1])
        c0.markdown(m["label"])
        c1.markdown(f"{currency} {m['week_1']:,.0f}")
        c2.markdown(f"{currency} {m['week_2']:,.0f}")
        c3.markdown(f"{currency} {m['week_3']:,.0f}")
        c4.markdown(f"{currency} {m['week_4']:,.0f}")
        c5.markdown(f"{currency} {m['total']:,.0f}")

    st.divider()

# ── ACADEMIC EXPLANATION ──────────────────────────────────────────────────────

with st.expander("📚 Hyperbolic Discounting — The Theory Behind This Module", expanded=False):
    st.markdown(
        """
        #### What is Present Bias?

        Standard economic models assume **exponential discounting** — people
        discount future rewards at a constant rate. If you prefer £100 today
        over £110 next week, you should also prefer £100 in 52 weeks over
        £110 in 53 weeks. The time gap is the same; the preference should
        be consistent.

        Behavioural economics shows this is not how people actually behave.
        Laibson (1997) demonstrated that people use **hyperbolic discounting**:
        they are very impatient in the short run but more patient in the long
        run. This creates time-inconsistent preferences — you plan to save
        next month but spend today.

        **The β-δ model** (Laibson, 1997):
        > *U = u(cₜ) + β × Σ δˢ u(cₜ₊ₛ)*

        Where β < 1 represents the present bias parameter — the extra
        weight placed on immediate rewards. A β of 0.7 means future utility
        is discounted by an additional 30% simply for not being immediate.

        #### Why it matters for personal finance

        O'Donoghue and Rabin (1999) showed that even mild present bias leads
        to systematic under-saving. People intend to save more starting next
        month — but next month, the same bias applies again. This is why
        automatic savings transfers (removing the decision entirely) are so
        effective: they bypass the present-biased choice architecture.

        #### What your index means

        The **Present Bias Index** in this module measures the ratio of
        Week 1 to Week 4 discretionary spending. Under exponential discounting
        with a stable income, this ratio should be approximately 1.0 —
        spending should be roughly uniform across the month.

        A ratio significantly above 1.0 is the observable signature of
        present bias in your personal financial data.

        *References:*
        - *Laibson, D. (1997). Golden Eggs and Hyperbolic Discounting. QJE.*
        - *O'Donoghue, T. & Rabin, M. (1999). Doing It Now or Later. AER.*
        - *Kahneman, D. & Tversky, A. (1979). Prospect Theory. Econometrica.*
        """
    )

render_footer()
