"""
pages/1_dashboard.py
WealthMind Africa — Transaction Ledger

This page is the data entry point for the application.
Every income and expense the user records here becomes the
raw material for all four economic analysis modules.

Structure:
    1. Auth guard       — redirect unauthenticated visitors
    2. Sidebar          — consistent navigation across all pages
    3. Monthly overview — key figures at a glance
    4. Add transaction  — form to record new income or expense
    5. Recent ledger    — the last 15 transactions
    6. Module previews  — signpost the four upcoming analysis modules
    7. Economic insight — one concept explained in plain language
"""

import streamlit as st
from datetime import datetime, date

from database.db import (
    get_current_balance,
    get_recent_transactions,
    get_monthly_summary,
    add_transaction,
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
)
from utils.sidebar import render_sidebar
from utils.footer  import render_footer

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Transactions — WealthMind Africa",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── AUTH GUARD ────────────────────────────────────────────────────────────────
# Every page in the pages/ folder starts with this check.
# If the user navigates directly to this URL without logging in,
# they see a clear message rather than a crash.

if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.page_link("app.py", label="← Go to Login")
    st.stop()   # st.stop() halts execution — nothing below this line runs

# ── CONVENIENCE VARIABLES ─────────────────────────────────────────────────────
# Pulled from session state once here so we do not repeat
# st.session_state.user["id"] throughout the file.

user    = st.session_state.user
user_id = user["id"]
currency = user.get("currency", "KES")
now     = datetime.now()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

render_sidebar("dashboard")

# Mobile navigation hint — hidden on desktop via CSS
st.markdown(
    '<div class="mobile-nav-hint">☰ &nbsp;Tap the arrow in the top-left to open navigation</div>',
    unsafe_allow_html=True,
)

# ── PAGE HEADER ───────────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='color: #00C49F;'>💳 Transaction Ledger</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Record your income and expenses here. "
    "Every entry you make improves the accuracy of the four economic analysis modules below."
)

st.divider()

# ── MONTHLY OVERVIEW ──────────────────────────────────────────────────────────
# Four key figures shown at the top — the most important numbers
# a user needs to see without scrolling.

balance = get_current_balance(user_id)
monthly = get_monthly_summary(user_id, now.year, now.month)
net     = monthly["net"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Current Balance",
        value=f"{currency} {balance:,.2f}",
    )

with col2:
    st.metric(
        label="📥 Income This Month",
        value=f"{currency} {monthly['total_income']:,.2f}",
    )

with col3:
    st.metric(
        label="📤 Expenses This Month",
        value=f"{currency} {monthly['total_expenses']:,.2f}",
    )

with col4:
    # Savings rate: what percentage of income was not spent this month.
    # This feeds directly into the Financial Health Score module.
    if monthly["total_income"] > 0:
        savings_rate = (net / monthly["total_income"]) * 100
        rate_label   = f"{savings_rate:.1f}% savings rate"
    else:
        savings_rate = 0
        rate_label   = "No income recorded yet"

    st.metric(
        label="📊 Net This Month",
        value=f"{currency} {abs(net):,.2f}",
        delta=rate_label,
        delta_color="normal" if net >= 0 else "inverse",
    )

st.divider()

# ── ADD TRANSACTION FORM ──────────────────────────────────────────────────────
# Placed inside an expander to keep the page uncluttered.
# The expander is open by default so new users see it immediately.

with st.expander("➕ Add a Transaction", expanded=True):

    with st.form("add_transaction_form", clear_on_submit=True):

        form_col1, form_col2 = st.columns(2)

        with form_col1:
            # Transaction type — income or expense
            txn_type = st.selectbox(
                "Type",
                options=["expense", "income"],
                format_func=lambda x: "📥 Income" if x == "income" else "📤 Expense",
            )

            # Date defaults to today but can be changed
            txn_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today(),   # Cannot log future transactions
            )

            txn_amount = st.number_input(
                f"Amount ({currency})",
                min_value=0.01,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="e.g. 5000",
                help="Enter the amount as a plain number — no commas or symbols. Example: 5000 for 5,000.",
            )

        with form_col2:
            # Category list changes depending on whether income or expense
            # is selected. We use a dynamic approach here.
            if txn_type == "income":
                category_options = INCOME_CATEGORIES
            else:
                category_options = EXPENSE_CATEGORIES

            txn_category = st.selectbox(
                "Category",
                options=category_options,
                format_func=lambda x: x.replace("_", " ").title(),
            )

            txn_description = st.text_input(
                "Description (optional)",
                placeholder="e.g. Monthly salary, Supermarket, Matatu fare",
                max_chars=100,
            )

        submitted = st.form_submit_button(
            "Save Transaction",
            use_container_width=True,
        )

    # Process the form submission outside the form block
    if submitted:
        if txn_amount is None or txn_amount <= 0:
            st.error("❌ Please enter an amount greater than zero.")
        else:
            success, message = add_transaction(
                user_id=user_id,
                date_str=str(txn_date),
                transaction_type=txn_type,
                category=txn_category,
                amount=txn_amount,
                description=txn_description,
            )

            if success:
                st.success(f"✅ Saved: {txn_category.replace('_', ' ').title()} — {currency} {txn_amount:,.2f}")
                st.rerun()   # Refresh the page so the new transaction appears immediately
            else:
                st.error(f"❌ {message}")

# ── RECENT TRANSACTIONS LEDGER ────────────────────────────────────────────────

st.markdown("### Recent Transactions")
st.caption("Showing your last 15 entries.")

transactions = get_recent_transactions(user_id, limit=15)

if transactions:
    # Display as a clean table using columns
    # Header row
    h1, h2, h3, h4, h5 = st.columns([1.5, 1.2, 2, 2, 3])
    h1.markdown("**Date**")
    h2.markdown("**Type**")
    h3.markdown("**Category**")
    h4.markdown("**Amount**")
    h5.markdown("**Description**")

    st.divider()

    for txn in transactions:
        c1, c2, c3, c4, c5 = st.columns([1.5, 1.2, 2, 2, 3])

        c1.markdown(txn["date"])

        # Colour-code income and expense labels
        if txn["type"] == "income":
            c2.markdown(":green[Income]")
            c4.markdown(f":green[+{currency} {txn['amount']:,.2f}]")
        else:
            c2.markdown(":red[Expense]")
            c4.markdown(f":red[-{currency} {txn['amount']:,.2f}]")

        c3.markdown(txn["category"].replace("_", " ").title())
        c5.markdown(txn["description"] if txn["description"] else "—")

    st.divider()

else:
    st.info(
        "No transactions recorded yet. "
        "Use the form above to add your first entry."
    )

# ── MODULE PREVIEWS ───────────────────────────────────────────────────────────
# These cards show what is coming in Weeks 2 and 3.
# They reinforce the educational purpose and make the app feel
# cohesive even before the modules are built.

st.divider()
st.markdown("### 🔬 Economic Analysis Modules")
st.markdown(
    "The transactions you record here are the input for four applied "
    "economics modules. Each module connects your personal financial data "
    "to a concept from the academic literature."
)

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left: 3px solid #00C49F;'>
            <strong>📊 Financial Health Score</strong><br><br>
            A composite index measuring your financial position across
            four dimensions grounded in economic theory.
            <br><br>
            <span style='color:#00C49F; font-size:0.85rem;'>
            Friedman (1957) · Deaton (1991) · Hall (1978)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p2:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left: 3px solid #00C49F;'>
            <strong>🇰🇪 Kenya Inflation Context</strong><br><br>
            Your spending in real terms, adjusted for Kenya's CPI.
            Distinguishes nominal from real value changes.
            <br><br>
            <span style='color:#00C49F; font-size:0.85rem;'>
            Fisher equation · KNBS CPI methodology
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p3:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left: 3px solid #00C49F;'>
            <strong>📈 Wealth Projection</strong><br><br>
            Three scenarios projecting your net worth at 10 and 25 years,
            demonstrating the compound effect of savings rate changes.
            <br><br>
            <span style='color:#00C49F; font-size:0.85rem;'>
            Solow growth model · Ramsey–Cass–Koopmans
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p4:
    st.markdown(
        """
        <div style='background:#1C2333; padding:1rem; border-radius:8px;
                    border-left: 3px solid #00C49F;'>
            <strong>🧠 Present Bias Detection</strong><br><br>
            Statistical analysis to detect hyperbolic discounting —
            a behavioural economics concept — in your own spending data.
            <br><br>
            <span style='color:#00C49F; font-size:0.85rem;'>
            Laibson (1997) · O'Donoghue &amp; Rabin (1999)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── ECONOMIC INSIGHT ──────────────────────────────────────────────────────────
# A short, plain-language explanation of one economic concept.
# This section appears on the dashboard to consistently remind the user
# (and any reader of the project) that this is an applied economics tool.

st.divider()

with st.expander("📚 Economic Insight — Why Categories Matter", expanded=False):
    st.markdown(
        """
        #### Controlled Vocabulary in Financial Data

        This ledger uses a fixed list of spending categories rather than
        allowing free-text input. This is a deliberate data design choice
        with an economic motivation.

        **In economics, meaningful aggregation requires consistent classification.**
        If one month you record a supermarket trip as *"food"* and the next month
        as *"groceries"*, the data cannot be reliably compared across time.
        The Kenya Inflation Context module, for example, compares your
        food spending this month against your food spending six months ago —
        that comparison is only valid if both entries use the same category label.

        This is the same principle behind how national statistics offices
        construct Consumer Price Index baskets: they track the same defined
        goods and services over time so that price changes reflect genuine
        inflation, not changes in what is being measured.

        > *"The first step in any empirical economic analysis is ensuring
        the data is consistently defined."*
        > — A principle applied in every major economic dataset, from the
        > World Bank's World Development Indicators to the Kenya National
        > Bureau of Statistics CPI reports.
        """
    )

render_footer()
