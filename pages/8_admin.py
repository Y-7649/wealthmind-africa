"""
pages/8_admin.py
WealthMind Africa — Admin Analytics Dashboard

SECURE, ADMIN-ONLY page. Gated by the is_admin flag on the user account and
hidden from the navigation of normal users (see utils/sidebar.py and the
showSidebarNavigation=false setting in .streamlit/config.toml).

Presents fully anonymised, cohort-level adoption and behavioural analytics —
the operational counterpart to the public School Impact Report. No individual
user is ever identified; every figure is an aggregate produced by
core/analytics.py.

Created by Yash Karia
"""

import streamlit as st
import plotly.graph_objects as go

from core.analytics import get_cohort_analytics
from utils.sidebar import render_sidebar
from utils.footer import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Admin Analytics — WealthMind Africa",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── AUTH GUARD (login + admin) ────────────────────────────────────────────────

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="← Go to Login")
    st.stop()

_user = st.session_state.get("user") or {}
if not _user.get("is_admin"):
    # Do not confirm the page exists to non-admins beyond a generic message.
    st.error("🔐 This page is restricted to administrator accounts.")
    st.page_link("app.py", label="← Return to Home")
    st.stop()

render_sidebar("admin")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── LOAD ANALYTICS (cached) ───────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner="Aggregating cohort analytics…")
def _load_cohort():
    return get_cohort_analytics()

c   = _load_cohort()
cur = c["primary_currency"]

# Manual refresh — analytics are cached for 5 minutes for performance
_hdr_l, _hdr_r = st.columns([4, 1])
with _hdr_l:
    st.markdown(
        """
        <div style="font-size:0.66rem; font-weight:700; color:#00C49F;
                    text-transform:uppercase; letter-spacing:0.16em; margin-bottom:0.3rem;">
            WealthMind Africa &nbsp;·&nbsp; Restricted &nbsp;·&nbsp; Anonymised
        </div>
        <h1 style="font-size:2.1rem; color:#E2E8F0; letter-spacing:-0.03em; margin:0 0 0.3rem 0;">
            🔐 Admin Analytics Dashboard
        </h1>
        <p style="color:#8899AA; font-size:0.92rem; max-width:680px; line-height:1.6; margin:0;">
            Cohort-level adoption and behavioural metrics across all registered users.
            Every figure is aggregated — no individual account is identifiable on this page.
        </p>
        """,
        unsafe_allow_html=True,
    )
with _hdr_r:
    if st.button("🔄 Refresh", use_container_width=True):
        _load_cohort.clear()
        st.rerun()

st.divider()

# ── HELPER: styled metric card ────────────────────────────────────────────────

def metric_card(col, label, value, sub="", colour="#E2E8F0"):
    col.markdown(
        f'<div style="background:linear-gradient(145deg,#1C2333,#161D2A);'
        f' border:1px solid #252D3D; border-radius:12px; padding:1.05rem 1.2rem;'
        f' height:100%;">'
        f'<div style="font-size:0.68rem; font-weight:600; color:#8899AA;'
        f' text-transform:uppercase; letter-spacing:0.07em; margin-bottom:0.4rem;">{label}</div>'
        f'<div style="font-size:1.6rem; font-weight:800; color:{colour};'
        f' letter-spacing:-0.02em; line-height:1; font-variant-numeric:tabular-nums;">{value}</div>'
        f'<div style="font-size:0.7rem; color:#445566; margin-top:0.35rem;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

PLOTLY_BG = "#0E1117"

def _style(fig, height=260, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#CCDDE8"), x=0),
        height=height,
        paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
        font=dict(color="#8899AA", size=11),
        margin=dict(t=40, b=35, l=50, r=20),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, color="#4A6070")
    fig.update_yaxes(showgrid=True, gridcolor="#1A2030", color="#4A6070")
    return fig

# ── ADOPTION METRICS ──────────────────────────────────────────────────────────

st.markdown("#### Adoption")

a1, a2, a3, a4 = st.columns(4)
metric_card(a1, "Registered Users", f"{c['n_users']:,}", "Total accounts", "#00C49F")
metric_card(a2, "Active — 7 days", f"{c['n_active_7d']:,}",
            f"{(c['n_active_7d']/c['n_users']*100):.0f}% of users" if c['n_users'] else "—")
metric_card(a3, "Active — 30 days", f"{c['n_active_30d']:,}",
            f"{(c['n_active_30d']/c['n_users']*100):.0f}% of users" if c['n_users'] else "—")
metric_card(a4, "Transactions Analysed", f"{c['n_transactions']:,}", "All recorded entries", "#00C49F")

b1, b2, b3, b4 = st.columns(4)
metric_card(b1, "Total Value Analysed", f"{cur} {c['value']['total']:,.0f}",
            f"Income + expenses ({cur})")
metric_card(b2, "Income Recorded", f"{cur} {c['value']['income']:,.0f}")
metric_card(b3, "Expenses Recorded", f"{cur} {c['value']['expense']:,.0f}", colour="#FF8800")
metric_card(b4, "Avg Transactions / User",
            f"{(c['n_transactions']/c['n_users']):.1f}" if c['n_users'] else "—")

st.divider()

# ── GROWTH CHARTS ─────────────────────────────────────────────────────────────

st.markdown("#### Growth")
g1, g2 = st.columns(2)

with g1:
    ug = c["user_growth"]
    if ug:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[r["month"] for r in ug], y=[r["cumulative"] for r in ug],
            mode="lines+markers", line=dict(color="#00C49F", width=2.5),
            marker=dict(size=6), fill="tozeroy", fillcolor="rgba(0,196,159,0.08)",
            hovertemplate="%{x}<br>%{y} total users<extra></extra>",
        ))
        st.plotly_chart(_style(fig, title="Cumulative Registered Users"), use_container_width=True)
    else:
        st.info("No registration history yet.")

with g2:
    tg = c["txn_growth"]
    if tg:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[r["month"] for r in tg], y=[r["count"] for r in tg],
            marker_color="#00C49F", marker_line_width=0,
            hovertemplate="%{x}<br>%{y} transactions<extra></extra>",
        ))
        st.plotly_chart(_style(fig, title="Transactions Recorded per Month"), use_container_width=True)
    else:
        st.info("No transaction history yet.")

st.divider()

# ── BEHAVIOURAL DISTRIBUTIONS ─────────────────────────────────────────────────

st.markdown("#### Behavioural & Financial Distributions")
st.caption(
    f"Computed from {c['health']['n_scored']} users with sufficient data for health scoring "
    f"and {c['bias']['n_measured']} users with measurable spending patterns."
)

d1, d2 = st.columns(2)

with d1:
    dist = c["health"]["score_distribution"]
    if c["health"]["n_scored"] > 0:
        labels = list(dist.keys())
        vals   = list(dist.values())
        fig = go.Figure(go.Bar(
            x=labels, y=vals,
            marker_color=["#FF4444", "#FF8800", "#00C49F"][:len(labels)],
            marker_line_width=0, text=vals, textposition="outside",
            hovertemplate="Score %{x}<br>%{y} users<extra></extra>",
        ))
        st.plotly_chart(
            _style(fig, title=f"Financial Health Score Distribution (avg {c['health']['avg_overall']:.0f}/100)"),
            use_container_width=True,
        )
    else:
        st.info("Not enough scored users yet for a health-score distribution.")

with d2:
    sv = c["health"]["savings_values"]
    if sv:
        fig = go.Figure(go.Histogram(
            x=sv, nbinsx=10, marker_color="#00C49F", marker_line_width=0,
            hovertemplate="%{x}% savings rate<br>%{y} users<extra></extra>",
        ))
        fig.add_vline(x=20, line_dash="dash", line_color="#7BC8A4",
                      annotation_text="20% benchmark", annotation_font_color="#7BC8A4")
        st.plotly_chart(
            _style(fig, title=f"Savings Rate Distribution (avg {c['health']['avg_savings_rate']:.1f}%)"),
            use_container_width=True,
        )
    else:
        st.info("Not enough data for a savings-rate distribution.")

e1, e2 = st.columns(2)

with e1:
    bv = c["bias"]["index_values"]
    if bv:
        fig = go.Figure(go.Histogram(
            x=bv, nbinsx=12, marker_color="#FF8800", marker_line_width=0,
            hovertemplate="Index %{x}<br>%{y} users<extra></extra>",
        ))
        fig.add_vline(x=1.1, line_dash="dash", line_color="#FFCC00",
                      annotation_text="bias threshold", annotation_font_color="#FFCC00")
        st.plotly_chart(
            _style(fig, title=f"Present Bias Index ({c['bias']['pct_present_bias']:.0f}% show bias)"),
            use_container_width=True,
        )
    else:
        st.info("Not enough data for a present-bias distribution.")

with e2:
    rd = c["resilience"]["distribution"]
    if c["health"]["n_scored"] > 0:
        labels = list(rd.keys())
        vals   = list(rd.values())
        # months bands: 0–1, 1–3, 3–6, 6+
        colours = ["#FF4444", "#FF8800", "#7BC8A4", "#00C49F"][:len(labels)]
        fig = go.Figure(go.Bar(
            x=labels, y=vals, marker_color=colours, marker_line_width=0,
            text=vals, textposition="outside",
            hovertemplate="%{x} months<br>%{y} users<extra></extra>",
        ))
        st.plotly_chart(
            _style(fig, title=f"Emergency-Fund Coverage (median {c['resilience']['median_months']:.1f} months)"),
            use_container_width=True,
        )
    else:
        st.info("Not enough data for a resilience distribution.")

st.divider()

# ── SPENDING & CURRENCY ───────────────────────────────────────────────────────

st.markdown("#### Spending Composition & Currency Mix")
f1, f2 = st.columns([1.6, 1])

with f1:
    cats = c["categories"]
    if cats:
        top = cats[:8][::-1]  # reverse for horizontal bar (largest on top)
        fig = go.Figure(go.Bar(
            x=[r["total"] for r in top],
            y=[r["category"].replace("_", " ").title() for r in top],
            orientation="h", marker_color="#00C49F", marker_line_width=0,
            text=[f"{r['pct']:.0f}%" for r in top], textposition="outside",
            textfont=dict(color="#7A9AB0", size=10),
            hovertemplate="%{y}: " + cur + " %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="Expense Value by Category (all users)", font=dict(size=13, color="#CCDDE8"), x=0),
            height=320, paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
            font=dict(color="#8899AA", size=11), showlegend=False,
            margin=dict(t=40, b=35, l=110, r=60),
            xaxis=dict(showgrid=True, gridcolor="#1A2030", color="#4A6070"),
            yaxis=dict(showgrid=False, color="#7A9AB0"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data recorded yet.")

with f2:
    curr = c["currencies"]
    if curr:
        fig = go.Figure(go.Pie(
            labels=[r["currency"] for r in curr],
            values=[r["count"] for r in curr],
            hole=0.55,
            marker=dict(colors=["#00C49F", "#4499FF", "#FF8800", "#8888FF", "#7BC8A4"]),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} users<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="Currency Distribution", font=dict(size=13, color="#CCDDE8"), x=0),
            height=320, paper_bgcolor=PLOTLY_BG, plot_bgcolor=PLOTLY_BG,
            font=dict(color="#8899AA", size=11),
            margin=dict(t=40, b=20, l=20, r=20), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No users yet.")

st.divider()

# ── AUTO-GENERATED FINDINGS ───────────────────────────────────────────────────

st.markdown("#### Auto-Generated Cohort Findings")
if c["insights"]:
    for ins in c["insights"]:
        st.markdown(
            f'<div style="background:#1C2333; border-left:3px solid #00C49F;'
            f' border-radius:0 8px 8px 0; padding:0.8rem 1.1rem; margin-bottom:0.6rem;'
            f' font-size:0.88rem; color:#CCDDE8; line-height:1.55;">{ins}</div>',
            unsafe_allow_html=True,
        )
else:
    st.info(
        "📋 Findings will appear automatically once at least 2 users have sufficient "
        "transaction history. The same engine powers the public School Impact Report."
    )

st.caption(
    "All statistics are aggregated across the full user base. No individual account "
    "is identifiable on this page. Analytics are cached for 5 minutes."
)

render_footer()
