"""
pages/00_assessment.py
WealthMind Africa — Financial Behaviour Assessment (public)

The primary entry point into the platform: a public, no-login, ~2-minute
behavioural economics assessment. One question per screen, progress bar,
back button, consent gate, and an instant premium results screen with a
screenshot-friendly share card.

This page is UI ONLY. All economics lives in the already-built, already-tested
engine:
    - core.assessment.score_assessment   (scoring — reuses the tracker's curves)
    - core.assessment.generate_assessment_insights
    - database.save_assessment           (one honest record, consented rows only)
    - database.get_assessment_scores     (existing analytics, for the percentile)

No new economic models, scoring systems, or analytics are introduced here.

Created by Yash Karia
"""

import streamlit as st

from core.assessment import (
    QUESTIONS,
    score_assessment,
    generate_assessment_insights,
    income_options,
    band_label,
    SCORE_EXPLANATIONS,
    STRENGTH_PHRASES,
    OPPORTUNITY_PHRASES,
)
from database.db import (
    save_assessment,
    get_assessment_scores,
    save_report_request,
    initialise_database,
)
from utils.styles import inject_global_styles
from utils.footer import render_footer
from utils.email_report import send_report_email

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="2-Minute Financial Behaviour Assessment — WealthMind Africa",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_global_styles()

# Ensure tables exist even when a visitor lands here directly from a QR / shared
# link without first hitting the home page. Cached so it runs once per process.
@st.cache_resource
def _init_db():
    initialise_database()

_init_db()

# Public deployment URL shown on the share card / used for QR codes.
# ▸▸ UPDATE this to your live Streamlit Cloud URL before printing QR codes ◂◂
ASSESSMENT_URL = "wealthmind-africa.streamlit.app"

# Minimum participants before the results page shows a cohort percentile.
MIN_FOR_PERCENTILE = 10

# ── PAGE-SCOPED STYLES (small, fast) ──────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Large, mobile-friendly option buttons */
    .main .stButton > button {
        padding: 0.85rem 1.1rem !important;
        font-size: 0.98rem !important;
        text-align: left !important;
        border: 1px solid #252D3D !important;
        background: linear-gradient(145deg,#141B28,#111620) !important;
        color: #DDE8F4 !important;
        font-weight: 500 !important;
    }
    .main .stButton > button:hover {
        border-color: rgba(0,196,159,0.5) !important;
        color: #FFFFFF !important;
    }
    /* Keep primary CTAs (Begin / Continue / Yes) teal and centred — this rule
       outranks the generic one above via the [kind] attribute. */
    .main .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#00C49F,#00A07F) !important;
        color: #062019 !important;
        text-align: center !important;
        border: none !important;
        font-weight: 700 !important;
    }
    /* Slim progress track */
    .asmt-bar {
        height: 6px; width: 100%;
        background: #161D2A; border-radius: 999px; overflow: hidden;
        margin: 0.2rem 0 0.4rem 0;
    }
    .asmt-bar-fill {
        height: 100%;
        background: linear-gradient(90deg,#00C49F,#00A07F);
        border-radius: 999px;
        transition: width 0.35s cubic-bezier(0.22,1,0.36,1);
    }
    .asmt-meta {
        font-size: 0.72rem; color:#4A6070; letter-spacing:0.06em;
        text-transform:uppercase;
    }
    /* Results: score grid */
    .score-grid {
        display:grid; grid-template-columns:repeat(2,1fr); gap:0.8rem; margin:1rem 0;
    }
    .score-tile {
        background:linear-gradient(145deg,#141B28,#111620);
        border:1px solid #1E2738; border-radius:12px; padding:1.1rem 1.2rem;
    }
    .score-tile .lbl {
        font-size:0.66rem; font-weight:700; color:#4A6070;
        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.4rem;
    }
    .score-tile .val { font-size:2rem; font-weight:800; letter-spacing:-0.03em; line-height:1; }
    .score-tile .band { font-size:0.74rem; font-weight:700; margin-top:0.2rem; }
    .score-tile .sub { font-size:0.72rem; color:#8899AA; margin-top:0.2rem; }
    /* Results: plain-English explanations */
    .explain-row { display:flex; gap:0.7rem; padding:0.5rem 0; border-bottom:1px solid #161D2A; }
    .explain-row:last-child { border-bottom:none; }
    .explain-name { color:#DDE8F4; font-weight:600; font-size:0.84rem; min-width:150px; }
    .explain-text { color:#8899AA; font-size:0.82rem; line-height:1.45; }
    @media (max-width:560px){
        .explain-row { flex-direction:column; gap:0.1rem; }
        .explain-name { min-width:0; }
    }
    /* Share card */
    .share-card {
        max-width:380px; margin:0.5rem auto;
        background:linear-gradient(160deg,#0F1824,#0A1018);
        border:1px solid rgba(0,196,159,0.25); border-radius:18px;
        padding:1.6rem 1.6rem 1.4rem; position:relative; overflow:hidden;
    }
    .share-card::before{
        content:''; position:absolute; top:0; left:0; right:0; height:3px;
        background:linear-gradient(90deg,transparent,#00C49F,transparent);
    }
    @media (min-width:640px){ .score-grid{ grid-template-columns:repeat(4,1fr);} }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── STATE ─────────────────────────────────────────────────────────────────────

ss = st.session_state
ss.setdefault("asmt_phase", "intro")     # intro | email | questions | results
ss.setdefault("asmt_qidx", 0)
ss.setdefault("asmt_answers", {"currency": "KES"})
ss.setdefault("asmt_saved", False)
ss.setdefault("asmt_result", None)
ss.setdefault("asmt_email", "")
ss.setdefault("asmt_send_ok", False)
ss.setdefault("asmt_show_share", False)

TOTAL = len(QUESTIONS)


def _reset():
    ss.asmt_phase = "intro"
    ss.asmt_qidx = 0
    ss.asmt_answers = {"currency": "KES"}
    ss.asmt_saved = False
    ss.asmt_result = None
    ss.asmt_email = ""
    ss.asmt_send_ok = False
    ss.asmt_show_share = False


def _valid_email(value: str) -> bool:
    value = (value or "").strip()
    return ("@" in value and "." in value.split("@")[-1]
            and len(value) >= 5 and " " not in value)


def _finalize():
    """
    Score, save the financial responses, store the email separately (linked by
    the internal assessment id), send the report, and move to results.
    Runs once (guarded) at the end of the question flow.
    """
    if ss.asmt_saved:
        ss.asmt_phase = "results"
        return

    record = score_assessment(ss.asmt_answers)
    email = ss.asmt_email

    # 1. Save the financial responses (always — research use disclosed upfront).
    assessment_id = save_assessment(record)

    # 2. Send the personalised report (best-effort; never blocks the results).
    send_ok = False
    try:
        send_ok, _ = send_report_email(email, record)
    except Exception:
        send_ok = False

    # 3. Store the email SEPARATELY, linked only by the internal id.
    try:
        save_report_request(assessment_id, email, record, sent=1 if send_ok else 0)
    except Exception:
        pass

    ss.asmt_saved = True
    ss.asmt_result = record
    ss.asmt_send_ok = send_ok
    ss.asmt_phase = "results"


# ── INTRO ─────────────────────────────────────────────────────────────────────

def render_intro():
    st.markdown(
        """
        <div class="wm-fade-1" style="text-align:center; padding:1.2rem 0 0.3rem;">
            <div style="font-size:0.7rem;font-weight:700;color:#00C49F;
                        text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;">
                WealthMind Africa &nbsp;·&nbsp; Research Assessment
            </div>
            <h1 style="font-size:1.9rem;color:#E2E8F0;letter-spacing:-0.03em;
                       line-height:1.22;margin:0 0 0.7rem;">
                How do people make financial decisions?
            </h1>
            <p style="color:#8899AA;font-size:0.95rem;line-height:1.6;max-width:540px;margin:0 auto;">
                WealthMind Africa is a behavioural economics platform studying how
                people save, spend, and make financial decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # What it measures
    st.markdown(
        """
        <div class="wm-fade-2" style="background:linear-gradient(145deg,#141B28,#111620);
             border:1px solid #1E2738;border-radius:14px;padding:1.1rem 1.3rem;margin:1.1rem 0 0.9rem;">
            <div style="font-size:0.66rem;font-weight:700;color:#4A6070;text-transform:uppercase;
                 letter-spacing:0.1em;margin-bottom:0.75rem;">This 2-minute assessment measures</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem 1rem;">
                <div style="color:#DDE8F4;font-size:0.92rem;">📊 &nbsp;Financial Health</div>
                <div style="color:#DDE8F4;font-size:0.92rem;">💰 &nbsp;Savings Habits</div>
                <div style="color:#DDE8F4;font-size:0.92rem;">🛡️ &nbsp;Financial Resilience</div>
                <div style="color:#DDE8F4;font-size:0.92rem;">🧠 &nbsp;Present Bias</div>
            </div>
        </div>
        <div class="wm-fade-3" style="color:#8899AA;font-size:0.86rem;line-height:1.6;
             text-align:center;max-width:540px;margin:0 auto 0.3rem;">
            Your results will be emailed to you after completion. Your financial
            responses are stored separately from your email address. Your anonymous
            responses contribute to ongoing research into financial decision-making.
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Start Assessment  →", use_container_width=True, type="primary", key="begin"):
            ss.asmt_phase = "email"
            st.rerun()


# ── EMAIL (required, before any questions) ────────────────────────────────────

def render_email():
    if st.button("←  Back", key="email_back"):
        ss.asmt_phase = "intro"
        st.rerun()

    st.markdown(
        """
        <div style="text-align:center;padding:0.8rem 0 0.2rem;">
            <h1 style="font-size:1.7rem;color:#E2E8F0;letter-spacing:-0.03em;
                       line-height:1.25;margin:0 0 0.6rem;">
                Where should we send your report?
            </h1>
            <p style="color:#8899AA;font-size:0.9rem;line-height:1.6;max-width:520px;margin:0 auto;">
                Your personalised assessment report will be emailed to you after
                completion. Your financial responses remain separate from your contact
                information. Your email may also be used to share future findings from
                the WealthMind Africa study.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    email = st.text_input(
        "Email address", key="entry_email", placeholder="you@example.com",
        value=ss.asmt_email, label_visibility="collapsed",
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Continue  →", use_container_width=True, type="primary", key="email_continue"):
            if _valid_email(email):
                ss.asmt_email = email.strip()
                ss.asmt_phase = "questions"
                ss.asmt_qidx = 0
                st.rerun()
            else:
                st.warning("Please enter a valid email address to continue.")
    st.caption("🔒 We never display your email, and it is never stored with your financial answers.")


# ── QUESTION ──────────────────────────────────────────────────────────────────

def render_question(q: dict):
    qidx = ss.asmt_qidx
    pct = int(qidx / TOTAL * 100)

    # Progress + back
    st.markdown(
        f'<div class="asmt-meta">{q.get("section","")}</div>'
        f'<div class="asmt-bar"><div class="asmt-bar-fill" style="width:{pct}%"></div></div>'
        f'<div class="asmt-meta">Question {qidx + 1} of {TOTAL}</div>',
        unsafe_allow_html=True,
    )

    if st.button("←  Back", key=f"back_{q['id']}"):
        if qidx > 0:
            ss.asmt_qidx -= 1
        else:
            ss.asmt_phase = "intro"
        st.rerun()

    st.markdown(
        f"<h2 style='font-size:1.45rem;color:#E2E8F0;margin:0.8rem 0 0.2rem;'>{q['prompt']}</h2>",
        unsafe_allow_html=True,
    )
    if q.get("subtitle"):
        st.markdown(
            f"<p style='color:#8899AA;font-size:0.88rem;margin:0 0 1rem;'>{q['subtitle']}</p>",
            unsafe_allow_html=True,
        )
    if q.get("concept"):
        st.markdown(
            f"<div style='font-size:0.68rem;color:#3A5060;margin-bottom:0.8rem;'>"
            f"Concept · {q['concept']}</div>",
            unsafe_allow_html=True,
        )

    # ── multi-select (pick two) ───────────────────────────────────────────────
    if q["kind"] == "multi2":
        codes = [o["code"] for o in q["options"]]
        labels = {o["code"]: o["label"] for o in q["options"]}
        picked = st.multiselect(
            "Pick your top two",
            options=codes,
            format_func=lambda c: labels[c],
            max_selections=2,
            default=ss.asmt_answers.get("categories", []),
            key=f"ms_{q['id']}",
        )
        if st.button("Continue  →", type="primary", key=f"next_{q['id']}",
                     disabled=(len(picked) != 2)):
            ss.asmt_answers["categories"] = picked
            _advance()
        if len(picked) != 2:
            st.caption("Select exactly two to continue.")
        return

    # ── consent gate ──────────────────────────────────────────────────────────
    if q["kind"] == "consent":
        for o in q["options"]:
            if st.button(o["label"], use_container_width=True, key=f"opt_{q['id']}_{o['code']}",
                         type="primary" if o["code"] == "yes" else "secondary"):
                ss.asmt_answers["consent"] = o["code"]
                _finalize()
                st.rerun()
        st.caption(
            "Either way you'll see your full results. Choosing *Yes* adds your "
            "anonymous responses to the study — no name, email, or identifying "
            "information is ever stored."
        )
        return

    # ── single choice ─────────────────────────────────────────────────────────
    # The income question's labels follow the currency picked on the previous
    # screen; the band codes (and therefore scoring) are identical regardless.
    options = q["options"]
    if q["id"] == "income":
        options = income_options(ss.asmt_answers.get("currency", "KES"))

    for o in options:
        if st.button(o["label"], use_container_width=True, key=f"opt_{q['id']}_{o['code']}"):
            ss.asmt_answers[q["id"]] = o["code"]
            _advance()

    if q.get("optional"):
        if st.button("Skip", key=f"skip_{q['id']}"):
            ss.asmt_answers[q["id"]] = None
            _advance()


def _advance():
    if ss.asmt_qidx < TOTAL - 1:
        ss.asmt_qidx += 1
        st.rerun()
    else:
        _finalize()
        st.rerun()


# ── RESULTS ───────────────────────────────────────────────────────────────────

def _verdict(rec: dict) -> str:
    h = rec["health_score"]
    if h >= 70:   base = "Strong financial habits"
    elif h >= 50: base = "Developing financial habits"
    elif h >= 30: base = "Early-stage financial habits"
    else:         base = "Financial habits that need attention"
    idx = rec["bias_index"]
    if idx >= 1.6:   tail = "with strong present bias"
    elif idx >= 1.1: tail = "with some present bias"
    else:            tail = "and time-consistent spending"
    return f"{base} {tail}."


def _score_colour(s: float) -> str:
    return "#00C49F" if s >= 70 else "#FF8800" if s >= 40 else "#FF4444"


def render_results():
    rec = ss.asmt_result

    # cohort percentile (reuses existing analytics data; display calc only)
    a_scores = get_assessment_scores()
    health_list = [r["health_score"] for r in a_scores if r["health_score"] is not None]
    percentile = None
    if len(health_list) >= MIN_FOR_PERCENTILE:
        below = sum(1 for s in health_list if s < rec["health_score"])
        percentile = round(below / len(health_list) * 100)

    # behavioural dimensions (key, display name, score) — drive the verdict
    dims = [
        ("savings",      "Savings rate",           rec["savings_score"]),
        ("resilience",   "Emergency buffer",       rec["resilience_score"]),
        ("consistency",  "Spending consistency",   rec["consistency_score"]),
        ("commitment",   "Investment commitment",  rec["commitment_score"]),
        ("present_bias", "Resisting present bias", rec["present_bias_score"]),
    ]
    strongest = max(dims, key=lambda d: d[2])
    weakest   = min(dims, key=lambda d: d[2])

    st.markdown(
        f"<div class='wm-fade-1' style='text-align:center;padding:0.5rem 0;'>"
        f"<div style='font-size:0.7rem;font-weight:700;color:#00C49F;"
        f"text-transform:uppercase;letter-spacing:0.16em;'>Your Results</div>"
        f"<h1 style='font-size:1.7rem;color:#E2E8F0;margin:0.5rem 0 0.2rem;'>{_verdict(rec)}</h1>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # four score tiles
    hc = _score_colour(rec["health_score"])
    pc = _score_colour(rec["present_bias_score"])
    rcl = _score_colour(rec["resilience_score"])
    sc = _score_colour(rec["savings_score"])
    st.markdown(
        f"""
        <div class="score-grid wm-fade-2">
          <div class="score-tile"><div class="lbl">Financial Health</div>
            <div class="val" style="color:{hc};">{rec['health_score']:.0f}</div>
            <div class="band" style="color:{hc};">{band_label(rec['health_score'])}</div>
            <div class="sub">out of 100</div></div>
          <div class="score-tile"><div class="lbl">Present Bias</div>
            <div class="val" style="color:{pc};">{rec['present_bias_score']:.0f}</div>
            <div class="band" style="color:{pc};">{band_label(rec['present_bias_score'])}</div>
            <div class="sub">{rec['present_bias_label']}</div></div>
          <div class="score-tile"><div class="lbl">Emergency Resilience</div>
            <div class="val" style="color:{rcl};">{rec['resilience_score']:.0f}</div>
            <div class="band" style="color:{rcl};">{band_label(rec['resilience_score'])}</div>
            <div class="sub">≈ {rec['emergency_fund_months']:.1f} months buffer</div></div>
          <div class="score-tile"><div class="lbl">Savings Rate</div>
            <div class="val" style="color:{sc};">{rec['savings_score']:.0f}</div>
            <div class="band" style="color:{sc};">{band_label(rec['savings_score'])}</div>
            <div class="sub">≈ {rec['savings_rate_pct']:.0f}% of income kept</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── VERDICT: strongest habit + biggest opportunity ───────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div style='background:rgba(0,196,159,0.06);border:1px solid rgba(0,196,159,0.2);"
            f"border-radius:10px;padding:0.9rem 1.1rem;height:100%;'>"
            f"<div style='font-size:0.65rem;color:#00C49F;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.1em;margin-bottom:0.35rem;'>💪 Strongest Financial Habit</div>"
            f"<div style='color:#DDE8F4;font-size:0.9rem;line-height:1.5;'>"
            f"Your strongest habit is {STRENGTH_PHRASES[strongest[0]]}.</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div style='background:rgba(255,136,0,0.06);border:1px solid rgba(255,136,0,0.2);"
            f"border-radius:10px;padding:0.9rem 1.1rem;height:100%;'>"
            f"<div style='font-size:0.65rem;color:#FF8800;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.1em;margin-bottom:0.35rem;'>🎯 Biggest Opportunity</div>"
            f"<div style='color:#DDE8F4;font-size:0.9rem;line-height:1.5;'>"
            f"Your biggest opportunity is {OPPORTUNITY_PHRASES[weakest[0]]}.</div></div>",
            unsafe_allow_html=True,
        )

    # ── WHAT YOUR SCORES MEAN (plain English) ─────────────────────────────────
    _expl = [
        ("Financial Health",     SCORE_EXPLANATIONS["health"]),
        ("Present Bias",         SCORE_EXPLANATIONS["present_bias"]),
        ("Spending Consistency", SCORE_EXPLANATIONS["consistency"]),
        ("Savings Rate",         SCORE_EXPLANATIONS["savings"]),
        ("Emergency Resilience", SCORE_EXPLANATIONS["resilience"]),
    ]
    _rows = "".join(
        f'<div class="explain-row"><div class="explain-name">{n}</div>'
        f'<div class="explain-text">{t}</div></div>' for n, t in _expl
    )
    st.markdown(
        f'<div style="background:#0F1824;border:1px solid #1E2738;border-radius:12px;'
        f'padding:0.7rem 1.1rem;margin:1rem 0;">'
        f'<div style="font-size:0.66rem;font-weight:700;color:#4A6070;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:0.2rem;">What your scores mean</div>'
        f'{_rows}</div>',
        unsafe_allow_html=True,
    )

    # one economic insight (the top insight from the existing engine)
    insights = generate_assessment_insights(rec)
    if insights:
        ins = insights[0]
        st.markdown(
            f"<div style='background:#141B28;border:1px solid #1E2738;border-left:3px solid #00C49F;"
            f"border-radius:0 12px 12px 0;padding:1.1rem 1.3rem;margin:1rem 0;'>"
            f"<div style='font-size:0.65rem;color:#00C49F;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.09em;margin-bottom:0.4rem;'>The economics · {ins['concept']}</div>"
            f"<div style='color:#CCDDE8;font-size:0.9rem;line-height:1.55;'>{ins['suggests']}</div>"
            f"<div style='color:#8899AA;font-size:0.84rem;line-height:1.5;margin-top:0.6rem;'>"
            f"<strong style='color:#00C49F;'>Try this:</strong> {ins['action']}</div></div>",
            unsafe_allow_html=True,
        )

    # cohort comparison
    if percentile is not None:
        st.markdown(
            f"<div style='text-align:center;color:#CCDDE8;font-size:0.95rem;margin:0.6rem 0 1rem;'>"
            f"📊 Your financial habits are stronger than "
            f"<strong style='color:#00C49F;'>{percentile}%</strong> of participants so far.</div>",
            unsafe_allow_html=True,
        )

    # ── SHARE CARD ────────────────────────────────────────────────────────────
    if percentile is not None:
        one_liner = f"Stronger financial habits than {percentile}% of participants."
    else:
        res_word = "above-average" if rec["resilience_score"] >= 50 else "limited"
        bias_word = ("strong" if rec["bias_index"] >= 1.6
                     else "some" if rec["bias_index"] >= 1.1 else "low")
        one_liner = f"{bias_word.capitalize()} present bias, {res_word} resilience."

    st.markdown("<h3 style='text-align:center;margin-top:0.5rem;'>Share your result</h3>",
                unsafe_allow_html=True)
    st.caption("📸 Screenshot the card below for WhatsApp, Instagram, or your group chat.")
    st.markdown(
        f"""
        <div class="share-card">
          <div style="font-size:0.72rem;font-weight:700;color:#00C49F;
                      text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.2rem;">
            🌍 WealthMind Africa
          </div>
          <div style="font-size:0.72rem;color:#4A6070;margin-bottom:1rem;">
            Financial Behaviour Assessment
          </div>
          <div style="display:flex;align-items:baseline;gap:0.5rem;">
            <div style="font-size:3.2rem;font-weight:800;color:{hc};line-height:1;
                        letter-spacing:-0.04em;">{rec['health_score']:.0f}</div>
            <div style="color:#8899AA;font-size:0.85rem;">/100<br>Financial Health</div>
          </div>
          <div style="display:flex;gap:1.5rem;margin-top:1rem;">
            <div><div style="font-size:0.62rem;color:#4A6070;text-transform:uppercase;
                 letter-spacing:0.08em;">Present Bias</div>
                 <div style="font-size:1.1rem;font-weight:700;color:{pc};">{rec['present_bias_label']}</div></div>
            <div><div style="font-size:0.62rem;color:#4A6070;text-transform:uppercase;
                 letter-spacing:0.08em;">Resilience</div>
                 <div style="font-size:1.1rem;font-weight:700;color:{rcl};">{rec['emergency_fund_months']:.1f} mo</div></div>
          </div>
          <div style="margin-top:1.1rem;padding-top:0.9rem;border-top:1px solid #1E2738;
                      color:#CCDDE8;font-size:0.86rem;font-style:italic;">
            "{one_liner}"
          </div>
          <div style="margin-top:1rem;font-size:0.7rem;color:#4A6070;">
            Take the 2-minute assessment · {ASSESSMENT_URL}/assessment
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── REPORT CONFIRMATION ───────────────────────────────────────────────────
    if ss.asmt_send_ok:
        st.success(f"📧 Your report has been sent to **{ss.asmt_email}**.")
    else:
        st.info("📧 Your report is being prepared and will be sent shortly.")

    # ── THANK YOU ─────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='text-align:center;background:linear-gradient(145deg,#0F1824,#0A1018);"
        "border:1px solid rgba(0,196,159,0.18);border-radius:14px;padding:1.3rem 1.4rem;"
        "margin:0.6rem 0 0.5rem;'>"
        "<div style='font-size:1.05rem;font-weight:700;color:#E2E8F0;margin-bottom:0.4rem;'>"
        "Thank you for participating in the WealthMind Africa assessment.</div>"
        "<div style='font-size:0.86rem;color:#8899AA;line-height:1.6;max-width:480px;margin:0 auto;'>"
        "Your responses contribute to ongoing research into financial decision-making "
        "across different ages and life stages.</div></div>",
        unsafe_allow_html=True,
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("📤 Share Assessment", use_container_width=True, key="ty_share"):
            ss.asmt_show_share = True
    with t2:
        st.page_link("pages/9_impact.py", label="📋 View Impact Report")
    with t3:
        if st.button("✓ Finish", use_container_width=True, key="ty_finish"):
            _reset()
            st.rerun()

    if ss.asmt_show_share:
        st.code(f"https://{ASSESSMENT_URL}/assessment", language=None)
        st.caption("Copy this link to invite others to take the assessment.")

    render_footer()


# ── ROUTER ────────────────────────────────────────────────────────────────────

if ss.asmt_phase == "intro":
    render_intro()
elif ss.asmt_phase == "email":
    render_email()
elif ss.asmt_phase == "questions":
    render_question(QUESTIONS[ss.asmt_qidx])
else:
    render_results()
