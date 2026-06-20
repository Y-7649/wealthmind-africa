"""
tools/seed_demo_cohort.py
WealthMind Africa — Demonstration Cohort Seeder

Populates a database with a synthetic student cohort so the Admin Analytics
Dashboard and School Impact Report can be demonstrated and screenshotted with
realistic data.

╔══════════════════════════════════════════════════════════════════════════╗
║ IMPORTANT — HONESTY NOTE                                                  ║
║ The accounts created here are SYNTHETIC. They exist only to demonstrate   ║
║ the dashboard layout and the analytics pipeline. They must NEVER be       ║
║ presented to anyone (admissions officers included) as real adoption.      ║
║ Real impact numbers must come from real students using the platform.      ║
║                                                                           ║
║ For that reason this script refuses to run against the default database.  ║
║ Point it at a throwaway file:                                             ║
║     DB_PATH=demo_cohort.db python tools/seed_demo_cohort.py               ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Refuse to touch the real database — demo data must stay isolated.
if not os.getenv("DB_PATH"):
    sys.exit(
        "Refusing to seed the default database.\n"
        "Run against a throwaway file, e.g.:\n"
        "    DB_PATH=demo_cohort.db python tools/seed_demo_cohort.py\n"
    )

# Ensure the project root is importable when run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import initialise_database, register_user, add_transaction  # noqa: E402

random.seed(42)  # reproducible cohort

N_STUDENTS = int(os.getenv("N_STUDENTS", "24"))
MONTHS     = 5

CURRENCIES = ["KES"] * 18 + ["USD"] * 3 + ["GBP"] * 2 + ["EUR"]  # KES-dominant

# Per-student behavioural archetypes — drive savings rate, present bias, buffer.
# (income, expense_ratio, week1_bias, savings_transfer_ratio)
ARCHETYPES = [
    # disciplined savers
    (90000, 0.70, 1.05, 0.10),
    (60000, 0.75, 1.10, 0.08),
    # average students with present bias
    (45000, 0.88, 1.45, 0.03),
    (30000, 0.92, 1.55, 0.02),
    (52000, 0.85, 1.35, 0.04),
    # stretched / vulnerable
    (25000, 0.98, 1.70, 0.00),
    (38000, 0.95, 1.60, 0.01),
    # strong
    (120000, 0.62, 1.02, 0.14),
]

EXPENSE_SPLIT = {
    "food":          0.34,
    "transport":     0.22,
    "rent":          0.16,
    "utilities":     0.09,
    "entertainment": 0.08,
    "education":     0.05,
    "health":        0.03,
    "other_expense": 0.03,
}
DISCRETIONARY = {"food", "transport", "entertainment", "other_expense"}


def _month_start(months_ago: int) -> datetime:
    today = datetime.now().replace(day=1)
    y, m = today.year, today.month - months_ago
    while m <= 0:
        m += 12
        y -= 1
    return datetime(y, m, 1)


def seed():
    initialise_database()
    total_txn = 0

    for i in range(N_STUDENTS):
        username = f"student_{i+1:02d}"
        currency = random.choice(CURRENCIES)
        ok, _ = register_user(username, "DemoPass1", currency=currency)
        if not ok:
            continue  # already seeded

        income, exp_ratio, w1_bias, save_ratio = random.choice(ARCHETYPES)
        # add a little per-student noise
        income     = int(income * random.uniform(0.85, 1.15))
        exp_ratio  = min(1.05, exp_ratio * random.uniform(0.95, 1.05))

        # fetch the new user's id via a fresh login-free lookup
        from database.db import get_connection
        conn = get_connection()
        uid = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()["id"]
        conn.close()

        for m_ago in range(MONTHS, 0, -1):
            start = _month_start(m_ago)
            # Income on day 1
            add_transaction(uid, start.strftime("%Y-%m-%d"), "income", "salary", float(income))
            total_txn += 1

            monthly_expense = income * exp_ratio
            # savings_transfer (investment commitment)
            if save_ratio > 0:
                add_transaction(uid, start.replace(day=2).strftime("%Y-%m-%d"),
                                "expense", "savings_transfer", round(income * save_ratio, 2))
                total_txn += 1

            # Week-selection weights that yield an average week1/week4 ratio ≈ w1_bias.
            # Every week keeps a positive share so the present-bias index stays
            # realistic (no near-empty final week producing an exploded ratio).
            week_weights = [
                w1_bias,                    # week 1
                1 + (w1_bias - 1) * 0.66,   # week 2
                1 + (w1_bias - 1) * 0.33,   # week 3
                1.0,                        # week 4
            ]
            week_day_ranges = [(1, 7), (8, 14), (15, 21), (22, 28)]

            for cat, share in EXPENSE_SPLIT.items():
                cat_total = monthly_expense * share
                n_entries = random.randint(4, 6)
                for _ in range(n_entries):
                    if cat in DISCRETIONARY:
                        wk = random.choices([0, 1, 2, 3], weights=week_weights, k=1)[0]
                        lo, hi = week_day_ranges[wk]
                        day = random.randint(lo, hi)
                    else:
                        day = random.randint(1, 28)
                    amount = round(cat_total / n_entries * random.uniform(0.8, 1.2), 2)
                    if amount <= 0:
                        continue
                    d = start.replace(day=min(day, 28))
                    add_transaction(uid, d.strftime("%Y-%m-%d"), "expense", cat, amount)
                    total_txn += 1

    print(f"Seeded {N_STUDENTS} students, {total_txn} transactions into {os.getenv('DB_PATH')}")


if __name__ == "__main__":
    seed()
