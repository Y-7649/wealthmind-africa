"""
pages/11_experiments.py
WealthMind Africa — Behavioural Lab  (Version 1.1 Experimental Module, public)

An OPTIONAL, ~60-second behavioural-finance mini-experiment: three short
scenarios exploring how people weigh time, windfalls, and inflation.

STRICT separation from the Version 1.0 research instrument:
    - answers are stored in their OWN table (v11_experiments)
    - nothing here is scored
    - nothing here touches the Financial Health, Present Bias, Savings,
      Spending Consistency or Resilience scores
    - responses are anonymous (no email, no name, no account link)

Created by Yash Karia
"""

import streamlit as st

from database.db import save_experiment_response, count_experiments
from utils.sidebar import render_sidebar
from utils.footer import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Behavioural Lab — WealthMind Africa",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="expanded",
)

render_sidebar("experiments")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

ss = st.session_state
ss.setdefault("exp_done", False)
ss.setdefault("exp_answers", {})

# ── SCENARIO DEFINITIONS ──────────────────────────────────────────────────────
# (code, label) options. Codes are what we persist; labels are what users see.

TIME_PREF = [
    ("today",   "KES 50,000 today"),
    ("delayed", "KES 60,000 one year from now"),
]
WINDFALL = [
    ("spend",  "Spend most of it"),
    ("save",   "Save most of it"),
    ("invest", "Invest most of it"),
    ("split",  "Split it between spending, saving and investing"),
]
REAL_NOMINAL = [
    ("better", "Better off"),
    ("worse",  "Worse off"),
    ("same",   "About the same"),
    ("unsure", "Not sure"),
]


def _radio(label, options, key):
    """A code-returning radio with no pre-selected answer (label kept for
    accessibility but visually collapsed — each scenario has its own heading)."""
    codes = [c for c, _ in options]
    labels = {c: l for c, l in options}
    return st.radio(label, codes, index=None,
                    format_func=lambda c: labels[c], key=key,
                    label_visibility="collapsed")


# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div style="padding:0.5rem 0 0.2rem;">
        <span class="wm-badge">🔬 &nbsp;Version 1.1 Experimental Module</span>
        <h1 style="font-size:1.9rem;color:#E2E8F0;letter-spacing:-0.03em;line-height:1.2;
                   margin:0.7rem 0 0.4rem;">Behavioural Lab</h1>
        <p style="color:#8899AA;font-size:0.95rem;line-height:1.6;max-width:560px;margin:0;">
            A 60-second mini-experiment on how people weigh time, windfalls, and
            inflation. This is <strong style="color:#CCDDE8;">separate</strong> from the
            2-minute assessment — your answers here are anonymous, are never scored,
            and never affect your Financial Health results.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ── EXPERIMENT ────────────────────────────────────────────────────────────────

if not ss.exp_done:
    st.markdown("##### 1 · Immediate vs delayed reward")
    st.caption("Would you rather receive:")
    a_time = _radio("time", TIME_PREF, "exp_time")

    st.markdown("##### 2 · An unexpected windfall")
    st.caption("You unexpectedly receive KES 50,000. What would you most likely do?")
    a_wind = _radio("windfall", WINDFALL, "exp_wind")

    st.markdown("##### 3 · Nominal vs real")
    st.caption("Your salary rises 8% this year, but prices rise 10%. Are you better off?")
    a_real = _radio("realnominal", REAL_NOMINAL, "exp_real")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("See what it says  →", use_container_width=True,
                     type="primary", key="exp_submit"):
            if None in (a_time, a_wind, a_real):
                st.warning("Please answer all three to continue.")
            else:
                record = {
                    "ans_time_pref": a_time,
                    "ans_windfall": a_wind,
                    "ans_real_nominal": a_real,
                }
                try:
                    save_experiment_response(record)
                except Exception:
                    pass   # never block the debrief on a storage hiccup
                ss.exp_answers = record
                ss.exp_done = True
                st.rerun()
    st.caption("Anonymous · not scored · contributes to Version 1.1 exploratory research.")

# ── DEBRIEF ───────────────────────────────────────────────────────────────────

else:
    ans = ss.exp_answers

    st.markdown(
        "<div style='text-align:center;padding:0.2rem 0 0.6rem;'>"
        "<div style='font-size:0.7rem;font-weight:700;color:#00C49F;text-transform:uppercase;"
        "letter-spacing:0.16em;'>Debrief</div>"
        "<h2 style='font-size:1.4rem;color:#E2E8F0;margin:0.4rem 0 0.2rem;'>"
        "What the choices reveal</h2></div>",
        unsafe_allow_html=True,
    )

    def _card(tag, title, body, highlight=False):
        border = "rgba(0,196,159,0.35)" if highlight else "#1E2738"
        st.markdown(
            f"<div style='background:linear-gradient(145deg,#141B28,#111620);"
            f"border:1px solid {border};border-radius:12px;padding:1rem 1.2rem;margin:0.5rem 0;'>"
            f"<div style='font-size:0.65rem;font-weight:700;color:#00C49F;text-transform:uppercase;"
            f"letter-spacing:0.1em;margin-bottom:0.3rem;'>{tag}</div>"
            f"<div style='color:#E2E8F0;font-weight:600;font-size:0.95rem;margin-bottom:0.3rem;'>{title}</div>"
            f"<div style='color:#9AA6B2;font-size:0.86rem;line-height:1.6;'>{body}</div></div>",
            unsafe_allow_html=True,
        )

    _card(
        "Present bias · hyperbolic discounting",
        "Immediate vs delayed reward",
        "Choosing KES 50,000 today over KES 60,000 in a year forgoes a 20% return — "
        "far above any bank deposit. Preferring the smaller-sooner reward is "
        "<em>present bias</em> (Laibson, 1997). Neither answer is wrong; the point is "
        "to notice the pull of “now.”"
        + ("<br><span style='color:#00C49F;'>You chose the delayed reward — patient with future value.</span>"
           if ans.get("ans_time_pref") == "delayed" else
           "<br><span style='color:#FF8800;'>You chose the reward today — a very human preference for the present.</span>"),
    )

    _card(
        "Mental accounting",
        "An unexpected windfall",
        "There's no wrong answer. Spending smooths consumption, saving builds a buffer, "
        "investing compounds, and splitting balances all three. Research finds people "
        "often treat “found” money more loosely than earned money — <em>mental "
        "accounting</em> (Thaler).",
    )

    correct = ans.get("ans_real_nominal") == "worse"
    _card(
        "Money illusion · real vs nominal",
        "Are you better off?",
        "An 8% raise with 10% inflation leaves you slightly <strong>worse off</strong> — "
        "real income falls about 1.8% (1.08 ÷ 1.10 − 1). Feeling richer from a bigger "
        "number while purchasing power falls is <em>money illusion</em> "
        "(Shafir, Diamond &amp; Tversky, 1997)."
        + ("<br><span style='color:#00C49F;'>You spotted it — real income actually fell.</span>"
           if correct else
           "<br><span style='color:#FF8800;'>Most people miss this one: the bigger number hides a real cut.</span>"),
        highlight=True,
    )

    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#8899AA;font-size:0.88rem;line-height:1.6;'>"
        "Want to see real vs nominal in action on your own numbers?</div>",
        unsafe_allow_html=True,
    )
    lc, rc = st.columns(2)
    with lc:
        st.page_link("pages/10_real_wealth.py", label="💡  Open Real vs Nominal Wealth")
    with rc:
        st.page_link("app.py", label="🏠  Back to Home")

    try:
        n = count_experiments()
        if n:
            st.caption(f"🔬 {n} people have explored the Behavioural Lab so far.")
    except Exception:
        pass

    if st.button("↺ Try again", key="exp_reset"):
        ss.exp_done = False
        ss.exp_answers = {}
        st.rerun()

render_footer()
