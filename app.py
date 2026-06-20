"""
app.py
WealthMind Africa — Entry Point

Created by Yash Karia
Contact: yashkaria.pro@gmail.com

This is the first file Streamlit executes when the application starts.

Responsibilities:
    1. Initialise session state (tracks who is logged in)
    2. Show the animated landing page with authentication for visitors
    3. Show the home dashboard for authenticated users
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

from database.db import (
    initialise_database,
    register_user,
    login_user,
    get_current_balance,
    get_recent_transactions,
    get_monthly_summary,
)
from utils.sidebar    import render_sidebar
from utils.footer     import render_footer
from utils.styles     import inject_global_styles
from utils.animations import get_animated_market_html
from core.insights    import generate_insights

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="WealthMind Africa",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject design system CSS immediately — covers both landing page and
# home dashboard.  render_sidebar() also calls this for all other pages.
# inject_global_styles() is called inside render_sidebar() on every page.
# On the landing page (no sidebar), we call it once here.
# On authenticated pages render_sidebar() handles it — do NOT call it again.
inject_global_styles()

# ── DATABASE INITIALISATION ───────────────────────────────────────────────────
# Cached with st.cache_resource so it runs once per server process,
# not on every page load or rerun.

@st.cache_resource
def _init_database():
    initialise_database()

_init_database()

# ── SESSION STATE ─────────────────────────────────────────────────────────────

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# Tracks which auth form is visible on the landing page: "login" or "register"
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"


# ── INPUT VALIDATION ──────────────────────────────────────────────────────────

def validate_username(username: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 20:
        return False, "Username must be 20 characters or fewer."
    if not username.replace("_", "").isalnum():
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, ""


# ── LANDING PAGE ──────────────────────────────────────────────────────────────

def show_landing_page():
    """
    Premium animated landing page shown to unauthenticated visitors.

    Layout:
        Nav bar       — project name left, Login/Register buttons right
        Hero section  — animated headline (left) + auth form (right)
        Canvas strip  — full-width animated wealth simulation
        Creator card  — Yash Karia profile
        Footer        — attribution
    """

    # ── TOP NAVIGATION BAR ────────────────────────────────────────────────────

    st.markdown(
        """
        <span style='font-size:1.3rem; font-weight:800; color:#00C49F;
                     letter-spacing:-0.025em;'>
            🌍 WealthMind Africa
        </span>
        <span style='font-size:0.76rem; color:#445566; margin-left:0.7rem;
                     letter-spacing:0.07em; text-transform:uppercase;
                     vertical-align:middle;'>
            Applied Economics Platform
        </span>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── HERO: headline (left) + auth form (right) ─────────────────────────────

    hero_col, auth_col = st.columns([1.6, 1], gap="large")

    # ── LEFT: Animated Headline + Feature Cards ───────────────────────────────
    with hero_col:

        # Badge — staggered entrance via CSS class
        st.markdown(
            """
            <div class="wm-fade-1" style="margin-bottom:0.7rem;">
                <span class="wm-badge">
                    🌍 &nbsp;Kenyan Economic Context &nbsp;·&nbsp; Academic Research
                </span>
            </div>

            <h1 class="wm-fade-2"
                style="font-size:2.45rem; color:#00C49F; line-height:1.18;
                       margin:0.5rem 0 0.4rem 0; letter-spacing:-0.03em;">
                Applying Economic Theory<br>to Personal Financial Behaviour
            </h1>

            <p class="wm-fade-3"
               style="color:#8899AA; font-size:1rem; line-height:1.68;
                      margin:0 0 1.3rem 0; max-width:510px;">
                Most personal finance apps record transactions.
                WealthMind Africa analyses them through the lens of
                <strong style="color:#CCDDE8;">economics</strong> and
                <strong style="color:#CCDDE8;">behavioural finance</strong> —
                distinguishing real from nominal value, detecting present bias,
                and projecting compound wealth trajectories.
            </p>
            """,
            unsafe_allow_html=True,
        )

        # Kenya Context CTA — public page link
        st.markdown(
            """
            <div class="wm-fade-3" style="margin-bottom:1rem;">
                <a href="/kenya_context" target="_self"
                   style="display:inline-flex; align-items:center; gap:0.5rem;
                          background:rgba(0,196,159,0.08);
                          border:1px solid rgba(0,196,159,0.3);
                          border-radius:8px; padding:0.5rem 1.1rem;
                          color:#00C49F; font-size:0.83rem; font-weight:600;
                          text-decoration:none; letter-spacing:0.02em;
                          transition:background 0.2s ease;">
                    🌍 &nbsp;Explore Kenya Economic Context
                    <span style="font-size:0.75rem; opacity:0.7;">— no account needed</span>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _pub_a, _pub_b = st.columns(2)
        with _pub_a:
            st.page_link("pages/0_kenya_context.py",
                         label="🌍  Kenya Economic Context")
            st.page_link("pages/7_findings.py",
                         label="📋  Economic Findings")
        with _pub_b:
            st.page_link("pages/9_impact.py",
                         label="📊  School Impact Report")
            st.page_link("pages/6_about.py",
                         label="👨‍💻  About the Researcher")

        # Four module cards — 2 × 2 grid
        # NOTE: Every opening HTML tag must close on the same line —
        # Streamlit's Markdown parser only recognises HTML blocks when
        # the opening tag's closing '>' is on the same line as '<div'.
        st.markdown(
            '<div class="wm-fade-4" style="display:grid; grid-template-columns:1fr 1fr; gap:0.65rem;">'

            '<div class="wm-card" style="padding:0.9rem;">'
            '<div style="font-size:0.93rem; font-weight:600; margin-bottom:0.35rem; color:#DDE8F4;">📊 Financial Health Score</div>'
            '<div style="color:#8899AA; font-size:0.79rem; line-height:1.55;">Composite index — savings rate, emergency fund, spending consistency, investment commitment.</div>'
            '<div style="margin-top:0.5rem; font-size:0.71rem; color:#3A5060; font-style:italic;">Friedman (1957) · Deaton (1991) · Hall (1978)</div>'
            '</div>'

            '<div class="wm-card" style="padding:0.9rem;">'
            '<div style="font-size:0.93rem; font-weight:600; margin-bottom:0.35rem; color:#DDE8F4;">🇰🇪 Kenya Inflation Context</div>'
            '<div style="color:#8899AA; font-size:0.79rem; line-height:1.55;">Fisher equation applied to personal spending. Real vs nominal using KNBS CPI data.</div>'
            '<div style="margin-top:0.5rem; font-size:0.71rem; color:#3A5060; font-style:italic;">Fisher equation · KNBS CPI methodology</div>'
            '</div>'

            '<div class="wm-card" style="padding:0.9rem;">'
            '<div style="font-size:0.93rem; font-weight:600; margin-bottom:0.35rem; color:#DDE8F4;">📈 Wealth Projection</div>'
            '<div style="color:#8899AA; font-size:0.79rem; line-height:1.55;">Compound growth over 25 years. Interactive savings rate slider. NSE-calibrated return assumptions.</div>'
            '<div style="margin-top:0.5rem; font-size:0.71rem; color:#3A5060; font-style:italic;">Solow growth model · Fisher (1930) · Modigliani (1954)</div>'
            '</div>'

            '<div class="wm-card" style="padding:0.9rem;">'
            '<div style="font-size:0.93rem; font-weight:600; margin-bottom:0.35rem; color:#DDE8F4;">🧠 Present Bias Detection</div>'
            '<div style="color:#8899AA; font-size:0.79rem; line-height:1.55;">Laibson\'s hyperbolic discounting model tested against your first-week vs last-week spending ratio.</div>'
            '<div style="margin-top:0.5rem; font-size:0.71rem; color:#3A5060; font-style:italic;">Laibson (1997) · O\'Donoghue &amp; Rabin (1999)</div>'
            '</div>'

            '</div>',
            unsafe_allow_html=True,
        )

    # ── RIGHT: Authentication Form ────────────────────────────────────────────
    with auth_col:

        # Subtle header above the tabs
        st.markdown(
            """
            <div style="text-align:center; padding:0.6rem 0 0.5rem 0;
                        background:linear-gradient(145deg,#141B28,#111620);
                        border-radius:10px 10px 0 0;
                        border:1px solid #1E2738; border-bottom:none;
                        margin-bottom:-1px;">
                <span style="color:#445566; font-size:0.76rem;
                             letter-spacing:0.07em; text-transform:uppercase;">
                    Access your financial analysis
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Form toggle — responds to the Login/Register nav buttons ──────────
        tog_a, tog_b = st.columns(2)
        with tog_a:
            if st.button(
                "🔑 Login",
                use_container_width=True,
                type="primary" if st.session_state.auth_view == "login" else "secondary",
                key="auth_tog_login",
            ):
                st.session_state.auth_view = "login"
                st.rerun()
        with tog_b:
            if st.button(
                "✏️ Register",
                use_container_width=True,
                type="primary" if st.session_state.auth_view == "register" else "secondary",
                key="auth_tog_register",
            ):
                st.session_state.auth_view = "register"
                st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Login ─────────────────────────────────────────────────────────────
        if st.session_state.auth_view == "login":
            with st.form("login_form", clear_on_submit=False):
                username  = st.text_input("Username",                  key="login_user")
                password  = st.text_input("Password", type="password", key="login_pass")
                submitted = st.form_submit_button(
                    "Login", use_container_width=True, type="primary"
                )

            if submitted:
                if not username or not password:
                    st.error("Please enter both fields.")
                else:
                    success, user_data = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user      = user_data
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")

        # ── Register ──────────────────────────────────────────────────────────
        else:
            _CURRENCY_LABELS = {
                "KES": "🇰🇪 KES — Kenyan Shilling",
                "USD": "🇺🇸 USD — US Dollar",
                "GBP": "🇬🇧 GBP — British Pound",
                "EUR": "🇪🇺 EUR — Euro",
                "INR": "🇮🇳 INR — Indian Rupee",
            }
            with st.form("register_form", clear_on_submit=True):
                new_user  = st.text_input("Choose a username",         key="reg_user")
                new_pass  = st.text_input("Choose a password",
                                          type="password",             key="reg_pass")
                conf_pass = st.text_input("Confirm password",
                                          type="password",             key="reg_conf")
                currency_choice = st.selectbox(
                    "Preferred currency",
                    options=list(_CURRENCY_LABELS.keys()),
                    format_func=lambda c: _CURRENCY_LABELS[c],
                    key="reg_currency",
                )

                st.caption(
                    "Username: 3–20 characters, letters/numbers/_ only.  \n"
                    "Password: 8+ characters, 1 uppercase, 1 number."
                )

                submitted = st.form_submit_button(
                    "Create Account", use_container_width=True, type="primary"
                )

            if submitted:
                valid_u, u_err = validate_username(new_user)
                valid_p, p_err = validate_password(new_pass)

                if not new_user or not new_pass:
                    st.error("Please fill in all fields.")
                elif not valid_u:
                    st.error(f"Username: {u_err}")
                elif not valid_p:
                    st.error(f"Password: {p_err}")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(new_user, new_pass, currency=currency_choice)
                    if ok:
                        st.success("Account created. Switch to Login to sign in.")
                        st.session_state.auth_view = "login"
                    else:
                        st.error(msg)

    # ── ANIMATED CANVAS CHART ─────────────────────────────────────────────────
    # Renders a Brownian-motion wealth simulation as a canvas animation.
    # Placed full-width so it creates a strong visual break before the
    # creator section.

    st.divider()

    # Pulsing dot + label
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.65rem;
                    margin-bottom:0.35rem;">
            <div style="width:7px; height:7px; border-radius:50%;
                        background:#00C49F;
                        box-shadow:0 0 8px rgba(0,196,159,0.9);
                        animation:dotPulse 2s ease-in-out infinite;
                        flex-shrink:0;"></div>
            <span style="color:#445566; font-size:0.74rem;
                         letter-spacing:0.1em; text-transform:uppercase;">
                Compound Wealth Simulation &nbsp;·&nbsp; Live
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components.html(get_animated_market_html(height=200), height=200)

    st.divider()

    # ── CREATOR SECTION ───────────────────────────────────────────────────────

    st.markdown(
        "<h3 style='margin-bottom:0.2rem;'>👨‍💻 About the Creator</h3>",
        unsafe_allow_html=True,
    )

    creator_left, creator_right = st.columns([2, 1])

    with creator_left:
        st.markdown(
            """
            WealthMind Africa was designed and built by **Yash Karia**, a student
            with a strong interest in Finance, Economics, Fintech, and Behavioural
            Finance.

            WealthMind Africa is an independent personal finance and applied
            economics platform, built to demonstrate how software can serve as
            a vehicle for genuine economic insight rather than simple transaction
            logging.

            The choice of a **Kenyan economic context** reflects a deliberate
            perspective: inflation dynamics, financial inclusion gaps, and
            mobile-money penetration in East Africa differ substantially from
            Western markets, and personal finance tools should reflect the
            reality of the market they serve.
            """
        )

    with creator_right:
        st.markdown(
            """
            <div class="wm-card wm-accent-left">
                <strong style="color:#FAFAFA; font-size:1rem;">Yash Karia</strong>
                <br><br>
                📧
                <a href="mailto:yashkaria.pro@gmail.com"
                   style="color:#00C49F; text-decoration:none;">
                    yashkaria.pro@gmail.com
                </a>
                <br><br>
                🐙
                <a href="https://github.com/Y-7649/wealthmind-africa"
                   target="_blank"
                   style="color:#00C49F; text-decoration:none; font-size:0.83rem;">
                    github.com/Y-7649/wealthmind-africa
                </a>
                <br><br>
                <span style="color:#8899AA; font-size:0.81rem; line-height:1.65;">
                    Finance · Economics · Fintech<br>
                    Behavioural Finance · Quantitative Analysis<br>
                    East African Markets
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_footer()


# ── HOME DASHBOARD ────────────────────────────────────────────────────────────

def show_home_dashboard():
    """
    Home dashboard shown to authenticated users after login.
    """
    render_sidebar("home")

    user     = st.session_state.user
    user_id  = user["id"]
    currency = user.get("currency", "KES")
    now      = datetime.now()

    # Mobile navigation hint — only visible on small screens via CSS
    st.markdown(
        '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
        unsafe_allow_html=True,
    )

    # Welcome header with staggered entrance animation
    st.markdown(
        f"""
        <div class="wm-fade-1">
            <h1 style="color:#00C49F; margin-bottom:0.15rem;">
                🌍 WealthMind Africa
            </h1>
        </div>
        <div class="wm-fade-2">
            <p style="color:#8899AA; margin-top:0; font-size:1rem;">
                Welcome back,
                <strong style="color:#FAFAFA;">{user['username']}</strong>.
                &nbsp;Financial overview for {now.strftime('%B %Y')}.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ECONOMIC TICKER ───────────────────────────────────────────────────────
    # Scrolling macro data strip — mirrors the Kenya Context page aesthetic.
    # Fetch summary data here so ticker and metric cards share one DB call.

    from data.kenya_cpi import get_current_inflation

    balance = get_current_balance(user_id)
    monthly = get_monthly_summary(user_id, now.year, now.month)

    _kenya_inf = get_current_inflation() * 100

    if monthly["total_income"] > 0:
        _sav_rate = (monthly["net"] / monthly["total_income"] * 100)
    else:
        _sav_rate = 0.0

    # Try to get Financial Health Score and Present Bias for the ticker
    try:
        from core.health_score import calculate_health_score
        _hs = calculate_health_score(user_id)
        _health_str = (
            f'<span style="color:#00C49F;font-weight:700;">{_hs["overall_score"]:.0f}/100</span>'
            if _hs.get("has_sufficient_data") else
            '<span style="color:#4A6070;font-weight:700;">—</span>'
        )
    except Exception:
        _health_str = '<span style="color:#4A6070;font-weight:700;">—</span>'

    try:
        from core.present_bias import calculate_present_bias
        _pb = calculate_present_bias(user_id, currency=currency)
        _bias_idx = _pb.get("bias_index", 0)
        _bias_col = "#FF8800" if _bias_idx > 1.1 else "#00C49F"
        _bias_str = (
            f'<span style="color:{_bias_col};font-weight:700;">{_bias_idx:.2f}</span>'
            if _pb.get("has_data") else
            '<span style="color:#4A6070;font-weight:700;">—</span>'
        )
    except Exception:
        _bias_str = '<span style="color:#4A6070;font-weight:700;">—</span>'

    _dash_ticker_items = [
        f'🇰🇪 KENYA INFLATION <span style="color:#FF8800;font-weight:700;">'
        f'{_kenya_inf:.1f}%</span>',
        f'YOUR SAVINGS RATE <span style="color:#00C49F;font-weight:700;">'
        f'{_sav_rate:.1f}%</span>',
        f'FINANCIAL HEALTH SCORE {_health_str}',
        f'PRESENT BIAS INDEX {_bias_str}',
        'CBK POLICY RATE <span style="color:#FF8800;font-weight:700;">9.75%</span>',
        'KENYA GDP GROWTH <span style="color:#00C49F;font-weight:700;">+5.4%</span>',
        'NSE RETURN ASSUMPTION <span style="color:#4499FF;font-weight:700;">7.0% p.a.</span>',
        'SSA INFLATION AVG <span style="color:#FF8800;font-weight:700;">14.0%</span>',
    ]
    _sep_t = '<span style="color:rgba(0,196,159,0.2);padding:0 0.5rem;font-size:0.65rem;">◆</span>'
    _ticker_content = _sep_t.join(
        f'<span style="font-family:Inter,monospace;font-size:0.76rem;font-weight:500;'
        f'color:#7A9AB0;padding:0 1.2rem;">{item}</span>'
        for item in _dash_ticker_items
    )
    # Duplicate for seamless CSS loop
    _ticker_content = _ticker_content + _sep_t + _ticker_content

    st.markdown(
        f"""
        <style>
        @keyframes dash-ticker-scroll {{
            0%   {{ transform: translateX(0); }}
            100% {{ transform: translateX(-50%); }}
        }}
        .dash-ticker-wrapper {{
            overflow: hidden;
            background: rgba(8,13,24,0.7);
            border: 1px solid rgba(0,196,159,0.1);
            border-radius: 8px;
            padding: 0.5rem 0;
            margin-bottom: 1.2rem;
        }}
        .dash-ticker-inner {{
            display: inline-block;
            white-space: nowrap;
            animation: dash-ticker-scroll 35s linear infinite;
        }}
        </style>
        <div class="dash-ticker-wrapper">
          <div class="dash-ticker-inner">{_ticker_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── SUMMARY METRICS — Animated Counters ──────────────────────────────────
    # JS-animated counters count from 0 to final value on page load.
    # Single components.html() block avoids iframe alignment issues.

    net = monthly["net"]
    _savings_rate_pct = (net / monthly["total_income"] * 100) if monthly["total_income"] > 0 else 0.0
    _net_colour   = "#00C49F" if net >= 0 else "#FF4444"
    _net_delta    = f"{_savings_rate_pct:.1f}% savings rate" if monthly["total_income"] > 0 else "No income recorded"
    _delta_colour = "#00C49F" if _savings_rate_pct >= 0 else "#FF4444"

    _metrics_html = f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0E1117; font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; padding:0; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; }}
.card {{
  background:linear-gradient(145deg,#1C2333 0%,#161D2A 100%);
  border:1px solid #252D3D; border-radius:12px;
  padding:1.1rem 1.3rem;
  transition:transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}}
.card:hover {{
  transform:translateY(-3px);
  border-color:rgba(0,196,159,0.45);
  box-shadow:0 8px 30px rgba(0,196,159,0.1),0 2px 8px rgba(0,0,0,0.3);
}}
.lbl {{
  font-size:0.7rem; font-weight:600; color:#8899AA;
  text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.45rem;
}}
.val {{
  font-size:1.45rem; font-weight:700; color:#FAFAFA;
  letter-spacing:-0.02em; line-height:1.1;
  font-variant-numeric:tabular-nums;
}}
.delta {{ font-size:0.75rem; margin-top:0.35rem; font-weight:500; }}
@media (max-width:550px) {{
  .grid {{ grid-template-columns:repeat(2,1fr); }}
  .val {{ font-size:1.2rem; }}
}}
</style></head><body>
<div class="grid">
  <div class="card">
    <div class="lbl">💰 Current Balance</div>
    <div class="val" id="v-bal" style="color:#E2E8F0;">{currency} 0.00</div>
  </div>
  <div class="card">
    <div class="lbl">📥 Income This Month</div>
    <div class="val" id="v-inc" style="color:#00C49F;">{currency} 0.00</div>
  </div>
  <div class="card">
    <div class="lbl">📤 Expenses This Month</div>
    <div class="val" id="v-exp" style="color:#FF8800;">{currency} 0.00</div>
  </div>
  <div class="card">
    <div class="lbl">📊 Net This Month</div>
    <div class="val" id="v-net" style="color:{_net_colour};">{currency} 0.00</div>
    <div class="delta" style="color:{_delta_colour};">{_net_delta}</div>
  </div>
</div>
<script>
var CUR = "{currency} ";
function fmt(n) {{
  return CUR + n.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});
}}
function animate(id, target, delay) {{
  setTimeout(function() {{
    var el = document.getElementById(id);
    var duration = 1400;
    var start = performance.now();
    function step(now) {{
      var progress = Math.min((now - start)/duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = fmt(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }}
    requestAnimationFrame(step);
  }}, delay);
}}
animate('v-bal', {balance:.6f},  80);
animate('v-inc', {monthly['total_income']:.6f}, 200);
animate('v-exp', {monthly['total_expenses']:.6f}, 320);
animate('v-net', {abs(net):.6f},  440);
</script></body></html>
"""
    components.html(_metrics_html, height=118)

    st.divider()

    # ── CATEGORY BREAKDOWN + RECENT TRANSACTIONS ──────────────────────────────

    left, right = st.columns([1, 1.8])

    with left:
        st.markdown("#### This Month by Category")
        if monthly["by_category"]:
            for cat, amount in sorted(
                monthly["by_category"].items(), key=lambda x: x[1], reverse=True
            ):
                proportion = (
                    amount / monthly["total_expenses"]
                    if monthly["total_expenses"] > 0 else 0
                )
                st.markdown(f"**{cat.replace('_', ' ').title()}**")
                st.progress(proportion,
                            text=f"{currency} {amount:,.2f} ({proportion:.0%})")
        else:
            st.info("No expenses recorded this month yet.")

    with right:
        st.markdown("#### Recent Transactions")
        transactions = get_recent_transactions(user_id, limit=10)
        if transactions:
            for txn in transactions:
                if txn["type"] == "income":
                    amount_str = f":green[+{currency} {txn['amount']:,.2f}]"
                else:
                    amount_str = f":red[-{currency} {txn['amount']:,.2f}]"
                cat_label = txn["category"].replace("_", " ").title()
                desc      = f" · {txn['description']}" if txn["description"] else ""
                st.markdown(
                    f"{txn['date']} &nbsp;|&nbsp; {amount_str} "
                    f"&nbsp;|&nbsp; {cat_label}{desc}"
                )
                st.divider()
        else:
            st.info(
                "No transactions yet.  \n"
                "Go to **Transactions** in the sidebar to add your first entry."
            )

    st.divider()

    # ── CROSS-MODULE INSIGHTS ─────────────────────────────────────────────────
    # Central analytical layer: connects behaviour, health, inflation,
    # and long-term projections into a unified economic analysis.

    insights = generate_insights(user_id, currency)

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.8rem;
                    margin-bottom:1.2rem;">
            <span style="font-size:1.4rem;">🔍</span>
            <div>
                <div style="font-size:1.1rem; font-weight:700; color:#FAFAFA;
                            letter-spacing:-0.01em;">
                    Cross-Module Economic Insights
                </div>
                <div style="font-size:0.8rem; color:#8899AA; margin-top:0.1rem;">
                    Connecting behaviour, health, inflation, and long-term outcomes
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not insights:
        st.info(
            "📋 **Insights will appear here** as you add more transactions.  \n"
            "The Cross-Module Insights Engine connects your savings rate, present "
            "bias, inflation context, and long-term projections into a unified "
            "economic analysis once you have at least 2 months of data."
        )
    else:
        _SEV_COLORS = {
            "critical": "#FF4444",
            "warning":  "#FF8800",
            "positive": "#00C49F",
            "info":     "#4499FF",
        }
        _SEV_LABELS = {
            "critical": "Critical",
            "warning":  "Warning",
            "positive": "Positive Signal",
            "info":     "Insight",
        }
        _PAGE_LABELS = {
            "pages/2_health_score.py": "Open Financial Health Score →",
            "pages/3_inflation.py":    "Open Kenya Inflation Context →",
            "pages/4_projection.py":   "Open Wealth Projection →",
            "pages/5_behaviour.py":    "Open Present Bias Detection →",
        }

        for ins in insights:
            c     = _SEV_COLORS.get(ins["severity"], "#4499FF")
            badge = _SEV_LABELS.get(ins["severity"], "Insight")

            # Build optional impact block before the main f-string
            if ins.get("impact"):
                ic = "#00C49F" if ins.get("impact_positive") else "#FF8800"
                imp_html = (
                    f'<div style="margin-top:0.75rem; padding:0.55rem 0.85rem;'
                    f' background:rgba(0,0,0,0.25); border-radius:6px;'
                    f' border-left:2px solid {ic};">'
                    f'<div style="font-size:0.67rem; color:#AAAAAA;'
                    f' text-transform:uppercase; letter-spacing:0.07em;'
                    f' margin-bottom:0.2rem;">Quantified Impact</div>'
                    f'<div style="font-size:0.84rem; color:#FAFAFA;'
                    f' line-height:1.5;">{ins["impact"]}</div></div>'
                )
            else:
                imp_html = ""

            st.markdown(
                f'<div style="background:#1C2333; border-radius:10px;'
                f' padding:1.2rem 1.4rem; border-left:4px solid {c};'
                f' margin-bottom:1rem;">'

                f'<div style="display:flex; justify-content:space-between;'
                f' align-items:flex-start; margin-bottom:0.85rem;">'
                f'<span style="font-size:1rem; font-weight:700; color:#FAFAFA;">'
                f'{ins["icon"]} {ins["title"]}</span>'
                f'<span style="font-size:0.69rem; color:{c}; font-weight:700;'
                f' text-transform:uppercase; letter-spacing:0.09em;'
                f' white-space:nowrap; margin-left:0.8rem;">{badge}</span></div>'

                f'<div style="margin-bottom:0.65rem;">'
                f'<div style="font-size:0.67rem; color:#445566;'
                f' text-transform:uppercase; letter-spacing:0.07em;'
                f' margin-bottom:0.2rem;">Observed</div>'
                f'<div style="font-size:0.88rem; color:#CCDDE8; line-height:1.56;">'
                f'{ins["observed"]}</div></div>'

                f'<div style="margin-bottom:0.65rem;">'
                f'<div style="font-size:0.67rem; color:#445566;'
                f' text-transform:uppercase; letter-spacing:0.07em;'
                f' margin-bottom:0.2rem;">Economic Concept</div>'
                f'<div style="font-size:0.83rem; color:#8899AA; line-height:1.5;">'
                f'{ins["concept"]}</div></div>'

                f'<div style="margin-bottom:0.3rem;">'
                f'<div style="font-size:0.67rem; color:#445566;'
                f' text-transform:uppercase; letter-spacing:0.07em;'
                f' margin-bottom:0.2rem;">Why It Matters</div>'
                f'<div style="font-size:0.83rem; color:#8899AA; line-height:1.5;">'
                f'{ins["why"]}</div></div>'

                f'{imp_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if ins.get("module_link"):
                lbl = _PAGE_LABELS.get(ins["module_link"], "Go deeper →")
                st.page_link(ins["module_link"], label=lbl)

    st.divider()

    # ── MODULE CARDS ──────────────────────────────────────────────────────────
    # Using .wm-card HTML class for hover-lift effect, with st.page_link()
    # below each card for navigation.

    st.markdown(
        "<h4 class='wm-fade-1' style='margin-bottom:0.8rem;'>"
        "Explore the Economic Modules</h4>",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            """
            <div class="wm-card wm-fade-1" style="min-height:115px;">
                <div style="font-size:1.55rem; margin-bottom:0.45rem;">📊</div>
                <div style="font-weight:600; font-size:0.88rem;
                            margin-bottom:0.3rem; color:#DDE8F4;">
                    Financial Health Score
                </div>
                <div style="color:#8899AA; font-size:0.78rem; line-height:1.45;">
                    Composite index across four economic dimensions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_health_score.py", label="Open →")

    with m2:
        st.markdown(
            """
            <div class="wm-card wm-fade-2" style="min-height:115px;">
                <div style="font-size:1.55rem; margin-bottom:0.45rem;">🇰🇪</div>
                <div style="font-weight:600; font-size:0.88rem;
                            margin-bottom:0.3rem; color:#DDE8F4;">
                    Kenya Inflation Context
                </div>
                <div style="color:#8899AA; font-size:0.78rem; line-height:1.45;">
                    Spending in real terms, adjusted for Kenya's CPI.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_inflation.py", label="Open →")

    with m3:
        st.markdown(
            """
            <div class="wm-card wm-fade-3" style="min-height:115px;">
                <div style="font-size:1.55rem; margin-bottom:0.45rem;">📈</div>
                <div style="font-weight:600; font-size:0.88rem;
                            margin-bottom:0.3rem; color:#DDE8F4;">
                    Wealth Projection
                </div>
                <div style="color:#8899AA; font-size:0.78rem; line-height:1.45;">
                    Net worth at 10 and 25 years under four compound-growth scenarios.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/4_projection.py", label="Open →")

    with m4:
        st.markdown(
            """
            <div class="wm-card wm-fade-4" style="min-height:115px;">
                <div style="font-size:1.55rem; margin-bottom:0.45rem;">🧠</div>
                <div style="font-weight:600; font-size:0.88rem;
                            margin-bottom:0.3rem; color:#DDE8F4;">
                    Present Bias Detection
                </div>
                <div style="color:#8899AA; font-size:0.78rem; line-height:1.45;">
                    Hyperbolic discounting detected in your spending data.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/5_behaviour.py", label="Open →")

    render_footer()


# ── ROUTER ────────────────────────────────────────────────────────────────────

if st.session_state.logged_in:
    show_home_dashboard()
else:
    show_landing_page()
