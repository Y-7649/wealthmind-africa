"""
pages/6_about.py
WealthMind Africa — About the Creator

Professional profile page for Yash Karia.
Explains the motivation, academic grounding, and design decisions
behind WealthMind Africa — written for a university admissions audience.
"""

import streamlit as st
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="About the Creator — WealthMind Africa",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

render_sidebar("about")

st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color:#00C49F;'>👨‍💻 About the Creator</h1>",
    unsafe_allow_html=True,
)

st.divider()

# ── PROFILE SECTION ───────────────────────────────────────────────────────────

profile_left, profile_right = st.columns([2, 1])

with profile_left:
    st.markdown(
        """
        ## Yash Karia

        I am a student with a strong interest in **Finance, Economics, Fintech,
        and Behavioural Finance**. My academic interests sit at the intersection
        of quantitative analysis, economic theory, and the application of
        technology to financial decision-making.

        WealthMind Africa is a personal project built to demonstrate that
        software can be a vehicle for genuine economic analysis — not just a
        tool for tracking transactions, but a platform for understanding *why*
        financial behaviour deviates from what economic theory would predict,
        and what the real-world consequences of those deviations are.
        """
    )

with profile_right:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1.5rem; border-radius:10px;
                    border:1px solid #2A2A3A;'>
            <div style='font-size:1.1rem; font-weight:bold;
                        color:#00C49F; margin-bottom:1rem;'>
                Contact
            </div>
            <div style='margin-bottom:0.6rem;'>
                📧
                <a href='mailto:yashkaria.pro@gmail.com'
                   style='color:#00C49F; text-decoration:none;'>
                    yashkaria.pro@gmail.com
                </a>
            </div>
            <div style='margin-bottom:0.6rem;'>
                🐙 GitHub
                <em style='color:#777777; font-size:0.85rem;'>
                <a href="https://github.com/Y-7649/wealthmind-africa"
                   target="_blank"
                   style="color:#00C49F; text-decoration:none;">
                    github.com/Y-7649/wealthmind-africa
                </a>
                </em>
            </div>
            <hr style='border-color:#2A2A3A; margin:1rem 0;'>
            <div style='color:#AAAAAA; font-size:0.85rem; line-height:1.6;'>
                <strong style='color:#CCCCCC;'>Interests</strong><br>
                Finance · Economics · Fintech<br>
                Behavioural Finance · Quantitative Analysis<br>
                Financial Technology · East African Markets
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── WHY I BUILT THIS ──────────────────────────────────────────────────────────

st.markdown("## Why I Built WealthMind Africa")

st.markdown(
    """
    Most personal finance applications solve a relatively simple problem:
    recording what you spent. WealthMind Africa was built to solve a more
    interesting problem — **understanding what your spending means**.

    WealthMind Africa was independently designed from the ground up as a
    personal economics platform — not a simple expense tracker. The core
    insight driving the design was that the most valuable questions in
    personal finance are not answered by transaction logs. They are answered
    by the concepts studied in Economics and Finance:

    - **Is your savings rate consistent with long-term wealth accumulation?**
      *(Permanent Income Hypothesis — Friedman, 1957)*
    - **How much of your spending increase reflects genuine consumption growth,
      and how much reflects inflation?**
      *(Real vs nominal distinction — Fisher equation)*
    - **Do you spend disproportionately more immediately after receiving income?**
      *(Present bias — Laibson, 1997)*
    - **What does your financial trajectory look like over 10 or 25 years
      under different savings rate scenarios?**
      *(Intertemporal choice and compound growth)*

    These are not software questions. They are economics questions. The project
    was built to make those questions answerable through real personal data.
    """
)

st.divider()

# ── THE KENYA CONTEXT ─────────────────────────────────────────────────────────

st.markdown("## Why a Kenyan Economic Context?")

st.markdown(
    """
    The decision to build WealthMind Africa specifically for the **Kenyan
    economic context** was deliberate and reflects a genuine perspective on
    how economics should be applied.

    Most personal finance platforms are designed for Western markets. They
    assume stable, low inflation environments; mature investment infrastructure;
    and financial inclusion levels that do not reflect the reality of most
    East African households.

    **Kenya presents a more economically interesting context:**

    - **Inflation dynamics** differ substantially from Western markets. Kenya
      experienced food inflation above 10% in 2022–2023, driven by global
      commodity prices and domestic supply disruptions. The distinction between
      nominal and real spending changes is not an academic exercise here —
      it has direct material consequences for household welfare.

    - **The NSE (Nairobi Securities Exchange)** provides a distinct risk-return
      environment from Western markets, with different correlation structures
      and emerging market premiums that make portfolio analysis more nuanced.

    - **The FinAccess Survey** (Central Bank of Kenya, 2021) shows that
      financial literacy and formal financial inclusion remain significantly
      below global averages — context that makes a financial education
      platform more valuable, not less.

    - **Mobile money penetration** (M-Pesa) has created unique patterns of
      financial behaviour in Kenya that differ from cash or card-based
      economies — a genuinely interesting area for behavioural analysis.

    Building for this specific context was also a statement: **economics is
    not universal, and financial tools should reflect the market they serve.**
    """
)

st.divider()

# ── HOW ECONOMIC THEORY IS APPLIED ───────────────────────────────────────────

st.markdown("## How WealthMind Africa Applies Economic Theory")

t1, t2 = st.columns(2)

with t1:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-left:3px solid #00C49F; margin-bottom:1rem;'>
            <strong>📊 Financial Health Score</strong><br><br>
            Operationalises four theoretical constructs into a single composite
            index — mirroring the methodology of credit bureaus and the World
            Bank's Financial Inclusion Index.<br><br>
            <em style='color:#AAAAAA; font-size:0.85rem;'>
            Grounded in: Friedman (1957), Deaton (1991), Hall (1978),
            Solow (1956)
            </em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-left:3px solid #00C49F;'>
            <strong>📈 Wealth Projection</strong><br><br>
            Demonstrates intertemporal choice through interactive compound
            growth scenarios. The visual gap between saving 10% vs 15% of
            income over 25 years makes abstract theory visceral.<br><br>
            <em style='color:#AAAAAA; font-size:0.85rem;'>
            Grounded in: Solow growth model, Fisher (1930) intertemporal choice,
            Modigliani (1954) life-cycle hypothesis
            </em>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t2:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-left:3px solid #00C49F; margin-bottom:1rem;'>
            <strong>🇰🇪 Kenya Inflation Context</strong><br><br>
            Applies the Fisher equation to personal transaction data —
            distinguishing nominal spending changes from real consumption
            changes using Kenya's actual CPI data from KNBS.<br><br>
            <em style='color:#AAAAAA; font-size:0.85rem;'>
            Grounded in: Fisher equation, macroeconomic price theory,
            KNBS Consumer Price Index methodology
            </em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='background:#1C2333; padding:1.2rem; border-radius:8px;
                    border-left:3px solid #00C49F;'>
            <strong>🧠 Present Bias Detection</strong><br><br>
            Tests Laibson's hyperbolic discounting model against the user's
            own spending data — detecting whether present bias is observable
            in their first-week vs last-week spending ratio.<br><br>
            <em style='color:#AAAAAA; font-size:0.85rem;'>
            Grounded in: Laibson (1997), O'Donoghue &amp; Rabin (1999)
            </em>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── ACADEMIC REFERENCES ───────────────────────────────────────────────────────

st.markdown("## Academic References")

st.markdown(
    """
    The following works directly inform the design and methodology of
    WealthMind Africa:

    - **Friedman, M. (1957).** *A Theory of the Consumption Function.*
      Princeton University Press.

    - **Hall, R.E. (1978).** Stochastic Implications of the Life Cycle–Permanent
      Income Hypothesis. *Journal of Political Economy, 86*(6), 971–987.

    - **Deaton, A. (1991).** Saving and Liquidity Constraints.
      *Econometrica, 59*(5), 1221–1248.

    - **Laibson, D. (1997).** Golden Eggs and Hyperbolic Discounting.
      *Quarterly Journal of Economics, 112*(2), 443–478.

    - **O'Donoghue, T. & Rabin, M. (1999).** Doing It Now or Later.
      *American Economic Review, 89*(1), 103–124.

    - **Lusardi, A. & Mitchell, O.S. (2014).** The Economic Importance of
      Financial Literacy. *Journal of Economic Literature, 52*(1), 5–44.

    - **Kenya National Bureau of Statistics.** *Consumer Price Index Monthly
      Reports.* KNBS, Nairobi.

    - **Central Bank of Kenya. (2021).** *FinAccess Household Survey.*
      CBK / KNBS / FSD Kenya.

    - **Modigliani, F. & Brumberg, R. (1954).** Utility Analysis and the Consumption
      Function. In K. Kurihara (ed.), *Post-Keynesian Economics.* Rutgers University Press.

    - **Suri, T. & Jack, W. (2016).** The long-run poverty and gender impacts of mobile money.
      *Science, 354*(6317), 1288–1292.

    - **Dupas, P. & Robinson, J. (2013).** Savings constraints and microenterprise development.
      *American Economic Review, 103*(4), 1138–1171.

    - **World Bank. (2024).** *Global Economic Prospects.*
      World Bank Group, Washington D.C.
    """
)

render_footer()
