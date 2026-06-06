"""
database/db.py
WealthMind Africa

This file is the single point of contact between the application
and the SQLite database. Every read and every write goes through
the functions defined here. No other file imports sqlite3 directly.

Sections:
    1. Connection
    2. Initialisation
    3. User operations   (register, login)
    4. Transaction operations (add, fetch, summarise)
    5. Health snapshot operations (save, fetch history)
"""

import os
import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime, date

# ── 1. CONNECTION ─────────────────────────────────────────────────────────────

# Path(__file__) is the absolute path to this file (db.py).
# .parent      is the database/ folder.
# .parent      again is the project root (wealthmind_africa/).
#
# DB_PATH checks the DB_PATH environment variable first.
# This allows cloud platforms (Railway) to redirect the database file
# to a persistent volume by setting DB_PATH=/data/wealthmind.db.
# Locally, no env var is set so it falls back to the project root.
_THIS_DIR = Path(__file__).parent
_DEFAULT_DB_PATH = _THIS_DIR.parent / "wealthmind.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_DEFAULT_DB_PATH)))
SCHEMA_PATH = _THIS_DIR / "schema.sql"


def get_connection():
    """
    Open and return a connection to the SQLite database.

    We set check_same_thread=False because Streamlit runs in a
    multi-threaded environment. SQLite handles this safely for a
    single-user application.

    We also enable foreign key enforcement — SQLite disables it
    by default, which would allow orphaned rows (e.g. transactions
    with no matching user). Enforcing it keeps the data consistent.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    # Return rows as dictionaries (column_name: value) instead of
    # plain tuples. This makes the code in every other file readable —
    # row["amount"] is clearer than row[2].
    conn.row_factory = sqlite3.Row

    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ── 2. INITIALISATION ─────────────────────────────────────────────────────────


def initialise_database():
    """
    Create all tables if they do not already exist.

    Reads the SQL from schema.sql and executes it. Running this on
    every application start is safe — all CREATE statements use
    IF NOT EXISTS, so existing data is never affected.
    """
    # pathlib.Path objects work directly with open() — no str() conversion needed
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()

    conn = get_connection()

    # executescript runs multiple SQL statements separated by semicolons
    conn.executescript(schema)
    conn.commit()
    conn.close()


# ── 3. USER OPERATIONS ────────────────────────────────────────────────────────

# Controlled vocabulary for valid transaction categories.
# Defined here so both db.py and the Streamlit UI use exactly the same list.
INCOME_CATEGORIES = ["salary", "freelance", "business", "other_income"]

EXPENSE_CATEGORIES = [
    "food",
    "transport",
    "rent",
    "utilities",
    "education",
    "health",
    "entertainment",
    "savings_transfer",
    "other_expense",
]


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Create a new user account.

    Arguments:
        username: The chosen username (3–20 characters, letters/numbers/_ only)
        password: The chosen password (validated before this function is called)

    Returns:
        (True, "success message")  if registration succeeded
        (False, "error message")   if it failed

    Security note:
        bcrypt.hashpw() generates a unique random salt automatically and
        incorporates it into the hash string. We never store the raw password —
        only the hash. This means even if someone reads the database file,
        they cannot recover users' passwords.
    """
    # Hash the password with bcrypt before storing it.
    # encode() converts the string to bytes, which bcrypt requires.
    # gensalt() generates a new random salt for each user.
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Store the hash as a string (decode from bytes back to str for SQLite)
    password_hash_str = password_hash.decode("utf-8")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash_str),
        )
        conn.commit()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        # IntegrityError is raised when the UNIQUE constraint on username fails
        return False, "Username already exists. Please choose another."

    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple[bool, dict | None]:
    """
    Verify login credentials.

    Arguments:
        username: The username entered by the user
        password: The password entered by the user

    Returns:
        (True, user_dict)   if credentials are correct
        (False, None)       if username not found or password wrong

    Security note:
        bcrypt.checkpw() compares the entered password against the stored hash.
        It is deliberately slow (work factor) to make brute-force attacks
        impractical. We return the same message whether the username is wrong
        or the password is wrong — this prevents an attacker from using error
        messages to discover valid usernames.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if row is None:
            # Username not found — return failure without revealing why
            return False, None

        # Compare the entered password against the stored bcrypt hash
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            row["password_hash"].encode("utf-8"),
        )

        if password_matches:
            # Convert the Row object to a plain dictionary for easy use
            return True, dict(row)
        else:
            return False, None

    finally:
        conn.close()


# ── 4. TRANSACTION OPERATIONS ─────────────────────────────────────────────────


def add_transaction(
    user_id: int,
    date_str: str,
    transaction_type: str,
    category: str,
    amount: float,
    description: str = "",
) -> tuple[bool, str]:
    """
    Insert a new transaction for a user.

    Arguments:
        user_id:          The logged-in user's ID (from the users table)
        date_str:         Date as a string in YYYY-MM-DD format
        transaction_type: 'income' or 'expense'
        category:         Must be from INCOME_CATEGORIES or EXPENSE_CATEGORIES
        amount:           Positive number (enforced by the database CHECK constraint)
        description:      Optional note about the transaction

    Returns:
        (True, "success message")
        (False, "error message")
    """
    # Validate the category against the controlled vocabulary
    all_categories = INCOME_CATEGORIES + EXPENSE_CATEGORIES
    if category not in all_categories:
        return False, f"Invalid category: {category}"

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO transactions (user_id, date, type, category, amount, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, date_str, transaction_type, category, amount, description),
        )
        conn.commit()
        return True, "Transaction recorded."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    finally:
        conn.close()


def get_recent_transactions(user_id: int, limit: int = 10) -> list[dict]:
    """
    Fetch the most recent transactions for a user.

    Arguments:
        user_id: The logged-in user's ID
        limit:   How many rows to return (default 10)

    Returns:
        A list of transaction dictionaries, most recent first.
        Empty list if no transactions exist yet.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT date, type, category, amount, description
            FROM   transactions
            WHERE  user_id = ?
            ORDER  BY created_at DESC
            LIMIT  ?
            """,
            (user_id, limit),
        ).fetchall()

        # Convert each Row object to a plain dictionary
        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_current_balance(user_id: int) -> float:
    """
    Calculate the user's current balance.

    Balance = sum of all income - sum of all expenses.

    This recalculates from the full transaction history each time.
    For the scale of this application (one user, hundreds of rows)
    this is fast enough. SQLite handles the aggregation efficiently.

    Returns:
        Current balance as a float. Returns 0.0 if no transactions exist.
    """
    conn = get_connection()
    try:
        # SUM income rows
        income_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'income'",
            (user_id,),
        ).fetchone()

        # SUM expense rows
        expense_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'expense'",
            (user_id,),
        ).fetchone()

        income_total = income_row["total"]
        expense_total = expense_row["total"]

        return income_total - expense_total

    finally:
        conn.close()


def get_monthly_summary(user_id: int, year: int, month: int) -> dict:
    """
    Return income, expenses, and a category breakdown for one calendar month.

    This is the core data function used by:
        - The Dashboard (current month summary)
        - The Financial Health Score (savings rate, investment commitment)
        - The Kenya Inflation Context (category-level spending)
        - The Present Bias module (weekly spending breakdown)

    Arguments:
        user_id: The logged-in user's ID
        year:    Four-digit year (e.g. 2025)
        month:   Month as an integer 1–12

    Returns a dictionary with this structure:
        {
            "total_income":   float,
            "total_expenses": float,
            "net":            float,   (income minus expenses)
            "by_category":    { "food": 3200.0, "transport": 800.0, ... }
        }
    """
    # Build the month prefix for date filtering: e.g. "2025-06"
    month_prefix = f"{year}-{month:02d}"

    conn = get_connection()
    try:
        # Total income for the month
        income_row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM   transactions
            WHERE  user_id = ? AND type = 'income' AND date LIKE ?
            """,
            (user_id, f"{month_prefix}%"),
        ).fetchone()

        # Total expenses for the month
        expense_row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM   transactions
            WHERE  user_id = ? AND type = 'expense' AND date LIKE ?
            """,
            (user_id, f"{month_prefix}%"),
        ).fetchone()

        # Expenses broken down by category
        category_rows = conn.execute(
            """
            SELECT   category, SUM(amount) AS total
            FROM     transactions
            WHERE    user_id = ? AND type = 'expense' AND date LIKE ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (user_id, f"{month_prefix}%"),
        ).fetchall()

        total_income = income_row["total"]
        total_expenses = expense_row["total"]
        by_category = {row["category"]: row["total"] for row in category_rows}

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": total_income - total_expenses,
            "by_category": by_category,
        }

    finally:
        conn.close()


def get_monthly_summaries_range(user_id: int, months: int = 6) -> list[dict]:
    """
    Return monthly summaries for the last N months.

    Used by the Kenya Inflation Context module to compare
    spending trends over time.

    Arguments:
        user_id: The logged-in user's ID
        months:  How many months back to retrieve (default 6)

    Returns:
        A list of monthly summary dictionaries, oldest first.
        Each dictionary has the same structure as get_monthly_summary()
        plus "year" and "month" keys.
    """
    results = []
    now = datetime.now()

    for i in range(months - 1, -1, -1):
        # Calculate the target month by stepping backwards
        # Using integer arithmetic to avoid datetime edge cases
        target_month = now.month - i
        target_year = now.year

        while target_month <= 0:
            target_month += 12
            target_year -= 1

        summary = get_monthly_summary(user_id, target_year, target_month)
        summary["year"] = target_year
        summary["month"] = target_month
        summary["month_label"] = f"{target_year}-{target_month:02d}"
        results.append(summary)

    return results


def get_weekly_spending(user_id: int, year: int, month: int) -> dict:
    """
    Break down discretionary expenses by week within a month.

    Used by the Present Bias Detection module. Discretionary categories
    are those where spending reflects choice rather than obligation.
    Fixed commitments (rent, utilities, education, health) are excluded
    because they do not reflect impulsive or present-biased behaviour.

    Arguments:
        user_id: The logged-in user's ID
        year:    Four-digit year
        month:   Month as an integer 1–12

    Returns:
        {
            "week_1": float,  (days 1–7)
            "week_2": float,  (days 8–14)
            "week_3": float,  (days 15–21)
            "week_4": float,  (days 22–end)
        }
    """
    # These categories reflect discretionary choice — relevant to present bias
    discretionary = ("food", "transport", "entertainment", "other_expense")

    month_prefix = f"{year}-{month:02d}"

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT date, amount
            FROM   transactions
            WHERE  user_id = ?
              AND  type = 'expense'
              AND  category IN ({})
              AND  date LIKE ?
            """.format(",".join("?" * len(discretionary))),
            (user_id, *discretionary, f"{month_prefix}%"),
        ).fetchall()

        # Bucket each transaction into weeks 1–4 by day of month
        weeks = {"week_1": 0.0, "week_2": 0.0, "week_3": 0.0, "week_4": 0.0}

        for row in rows:
            day = int(row["date"].split("-")[2])

            if day <= 7:
                weeks["week_1"] += row["amount"]
            elif day <= 14:
                weeks["week_2"] += row["amount"]
            elif day <= 21:
                weeks["week_3"] += row["amount"]
            else:
                weeks["week_4"] += row["amount"]

        return weeks

    finally:
        conn.close()


# ── 5. HEALTH SNAPSHOT OPERATIONS ─────────────────────────────────────────────


def save_health_snapshot(user_id: int, scores: dict) -> None:
    """
    Save a Financial Health Score snapshot for today.

    Called each time the user views the Health Score page.
    Duplicate entries for the same date are intentionally allowed —
    the user may improve their score during a single day, and
    seeing intra-day progress is useful.

    Arguments:
        user_id: The logged-in user's ID
        scores:  Dictionary produced by core/health_score.py containing
                 all score dimensions and their raw values.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO health_snapshots (
                user_id,
                overall_score,
                savings_rate_score,
                emergency_fund_score,
                consistency_score,
                commitment_score,
                savings_rate_pct,
                emergency_fund_months,
                spending_cv,
                commitment_rate_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                scores.get("overall_score"),
                scores.get("savings_rate_score"),
                scores.get("emergency_fund_score"),
                scores.get("consistency_score"),
                scores.get("commitment_score"),
                scores.get("savings_rate_pct"),
                scores.get("emergency_fund_months"),
                scores.get("spending_cv"),
                scores.get("commitment_rate_pct"),
            ),
        )
        conn.commit()

    finally:
        conn.close()


def get_health_snapshot_history(user_id: int, limit: int = 30) -> list[dict]:
    """
    Fetch the most recent health score snapshots for a user.

    Used to draw the Health Score trend line on the Health Score page.

    Arguments:
        user_id: The logged-in user's ID
        limit:   Maximum number of snapshots to return (default 30)

    Returns:
        A list of snapshot dictionaries, oldest first (for charting).
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT   snapshot_date, overall_score,
                     savings_rate_score, emergency_fund_score,
                     consistency_score, commitment_score
            FROM     health_snapshots
            WHERE    user_id = ?
            ORDER BY snapshot_date ASC, id ASC
            LIMIT    ?
            """,
            (user_id, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
