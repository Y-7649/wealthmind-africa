# WealthMind Africa

**Applying Economic Theory to Personal Financial Behaviour**

Created by **Yash Karia**
Contact: [yashkaria.pro@gmail.com](mailto:yashkaria.pro@gmail.com)

---

## Overview

WealthMind Africa is a personal finance platform built specifically for the **Kenyan economic context**. It applies concepts from economics and behavioural finance to help users understand not just what they spent, but what their financial behaviour means — and what it implies for their long-term wealth.

Most personal finance applications record transactions. WealthMind Africa analyses them through the lens of economic theory: distinguishing nominal from real spending changes, detecting present bias in spending patterns, scoring financial health using composite index methodology, and projecting wealth trajectories using compound growth models.

> *"The goal is not to build a budgeting app. The goal is to make economic concepts tangible through real personal data."*

---

## The Four Economic Modules

### 📊 Financial Health Score
A composite index (0–100) across four dimensions, each grounded in economic theory:

| Dimension | Economic Basis |
|---|---|
| Savings Rate | Friedman's Permanent Income Hypothesis (1957) |
| Emergency Fund | Buffer stock saving theory — Deaton (1991) |
| Spending Consistency | Consumption smoothing — Hall (1978) |
| Investment Commitment | Capital accumulation — Solow growth model |

### 🇰🇪 Kenya Inflation Context
Applies the **Fisher equation** to personal transaction data. Shows the difference between nominal spending changes (what you see) and real spending changes (what they mean), using Kenya's actual CPI data from the Kenya National Bureau of Statistics.

```
Real change = ((1 + nominal change) / (1 + inflation rate)) - 1
```

### 📈 Wealth Projection
Four compound-growth scenarios projected over 25 years — demonstrating the intertemporal consequences of savings rate decisions. An interactive slider allows users to explore how marginal changes in savings rate affect long-term wealth.

### 🧠 Present Bias Detection
Tests **Laibson's (1997) hyperbolic discounting model** against the user's own spending data. Computes the ratio of first-week to last-week discretionary spending — the observable signature of present bias.

---

## Academic Foundation

This project is grounded in the following literature:

- Friedman, M. (1957). *A Theory of the Consumption Function.* Princeton University Press.
- Modigliani, F. & Brumberg, R. (1954). Utility Analysis and the Consumption Function. *Post-Keynesian Economics.*
- Suri, T. & Jack, W. (2016). The long-run poverty and gender impacts of mobile money. *Science, 354*(6317).
- Hall, R.E. (1978). Stochastic Implications of the Life Cycle–Permanent Income Hypothesis. *JPE, 86*(6).
- Deaton, A. (1991). Saving and Liquidity Constraints. *Econometrica, 59*(5).
- Laibson, D. (1997). Golden Eggs and Hyperbolic Discounting. *QJE, 112*(2).
- O'Donoghue, T. & Rabin, M. (1999). Doing It Now or Later. *AER, 89*(1).
- Lusardi, A. & Mitchell, O.S. (2014). The Economic Importance of Financial Literacy. *JEL, 52*(1).
- Kenya National Bureau of Statistics. *CPI Monthly Reports.*
- Central Bank of Kenya. (2021). *FinAccess Household Survey.*

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web Interface | Streamlit |
| Database | SQLite (via Python stdlib) |
| Charts | Plotly |
| Authentication | bcrypt |
| Data | KNBS CPI (hardcoded), World Bank |

---

## Project Structure

```
wealthmind_africa/
│
├── app.py                    # Entry point — landing page and home dashboard
│
├── database/
│   ├── schema.sql            # Relational database design (4 tables)
│   └── db.py                 # All database operations
│
├── core/
│   ├── health_score.py       # Financial Health Score engine
│   ├── inflation.py          # Kenya Inflation Context engine
│   ├── projection.py         # Wealth Projection engine
│   ├── present_bias.py       # Present Bias Detection engine
│   └── insights.py           # Cross-Module Economic Insights engine
│
├── pages/
│   ├── 0_kenya_context.py    # Public Kenya Economic Context dashboard
│   ├── 1_dashboard.py        # Transaction ledger
│   ├── 2_health_score.py     # Financial Health Score page
│   ├── 3_inflation.py        # Kenya Inflation Context page
│   ├── 4_projection.py       # Wealth Projection page
│   ├── 5_behaviour.py        # Present Bias Detection page
│   └── 6_about.py            # About the Creator
│
├── data/
│   ├── kenya_cpi.py          # KNBS CPI data and helper functions
│   └── kenya_macro.py        # Kenya macro indicators for public dashboard
│
├── utils/
│   ├── sidebar.py            # Shared sidebar component
│   └── footer.py             # Shared footer component
│
├── .streamlit/
│   └── config.toml           # Dark theme configuration
│
├── requirements.txt
└── README.md
```

---

## Setup & Installation

**Requirements:** Python 3.9+

```bash
# Clone the repository
git clone https://github.com/Y-7649/wealthmind-africa.git
cd wealthmind-africa

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m streamlit run app.py
```

The app opens at `http://localhost:8501`. Register an account and start recording transactions to activate the economic analysis modules.

---

## Data Requirements per Module

| Module | Minimum Data Needed |
|---|---|
| Financial Health Score | 1 month of income + expenses |
| Kenya Inflation Context | 2 months of expenses |
| Wealth Projection | 1 month of income |
| Present Bias Detection | 1 month of discretionary spending |

---

## Why Kenya?

Kenya presents a more economically interesting context than Western markets:

- Inflation dynamics differ substantially — food inflation exceeded 10% in 2022–2023
- The NSE provides an emerging market risk-return profile distinct from Western indices
- Financial inclusion gaps (FinAccess Survey, 2021) make financial education tools especially valuable
- Mobile money penetration (M-Pesa) creates unique behavioural patterns worth studying

Building for this specific context reflects a core belief: **economic tools should reflect the market they serve.**

---

## Creator

**Yash Karia**
📧 [yashkaria.pro@gmail.com](mailto:yashkaria.pro@gmail.com)
🐙 GitHub: [github.com/Y-7649/wealthmind-africa](https://github.com/Y-7649/wealthmind-africa)

*Interests: Finance · Economics · Fintech · Behavioural Finance · Quantitative Analysis · East African Markets*

---

*WealthMind Africa — Applying Economic Theory to Personal Financial Behaviour*
