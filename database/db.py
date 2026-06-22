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
from datetime import datetime, date, timedelta

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


# ── TURSO (libSQL) SUPPORT ────────────────────────────────────────────────────
# Streamlit Community Cloud has an ephemeral filesystem, so a local SQLite file
# is wiped on every restart. When TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are
# provided (via environment variables or Streamlit secrets), every connection is
# routed to a hosted Turso database instead, which persists permanently.
#
# Turso speaks SQLite, so NONE of the SQL in this file changes. The only shim
# needed is to preserve the dict-style row access (row["col"], dict(row)) the
# rest of the codebase relies on — the libSQL client returns plain tuples, so a
# thin adapter re-wraps rows as dicts. Nothing outside get_connection() changes.


def _turso_credentials():
    """
    Return (url, token) for Turso if configured, else (None, None).

    Checks environment variables first, then Streamlit secrets — the secrets
    lookup is wrapped so it never raises outside a Streamlit runtime (e.g. in
    unit tests or CLI usage).
    """
    url   = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    if not (url and token):
        try:
            import streamlit as st
            url   = url   or st.secrets.get("TURSO_DATABASE_URL")
            token = token or st.secrets.get("TURSO_AUTH_TOKEN")
        except Exception:
            pass
    return url, token


def _split_sql_script(script: str) -> list:
    """
    Split a multi-statement SQL script into individual statements, dropping SQL
    line comments and blank statements. Lets the libSQL adapter run schema.sql
    without relying on a native executescript().
    """
    statements = []
    for chunk in script.split(";"):
        lines = [ln for ln in chunk.splitlines() if not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements


class _DictCursor:
    """
    Wraps a libSQL cursor so fetched rows come back as plain dicts — preserving
    the row["col"] and dict(row) access used throughout this file.
    """

    def __init__(self, cursor):
        self._c = cursor

    def _columns(self):
        return [d[0] for d in self._c.description] if self._c.description else []

    def fetchone(self):
        row = self._c.fetchone()
        if row is None:
            return None
        cols = self._columns()
        return {col: row[i] for i, col in enumerate(cols)}

    def fetchall(self):
        cols = self._columns()
        return [{col: row[i] for i, col in enumerate(cols)} for row in self._c.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())

    @property
    def lastrowid(self):
        return self._c.lastrowid

    @property
    def rowcount(self):
        return self._c.rowcount


class _TursoConnection:
    """
    Minimal sqlite3-style connection backed by Turso/libSQL. Implements only the
    surface this codebase uses: execute, executescript, commit, close — returning
    dict rows so no other function in this file needs to change.
    """

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=()):
        cur = self._conn.cursor()
        cur.execute(sql, tuple(params))
        return _DictCursor(cur)

    def executescript(self, script):
        cur = self._conn.cursor()
        for stmt in _split_sql_script(script):
            cur.execute(stmt)
        return _DictCursor(cur)

    def commit(self):
        self._conn.commit()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


def _connect_turso(url: str, token: str) -> "_TursoConnection":
    """
    Open a REMOTE-ONLY connection to the hosted Turso database (write-through to
    the cloud — the correct model for an ephemeral host, no local replica file).

    Prefers the `libsql` package (ships manylinux wheels for cp311–cp313, so it
    installs on Streamlit Cloud's Python) and falls back to `libsql-experimental`
    if that's what happens to be installed. Fails loudly if neither is present,
    so data is never silently written to ephemeral storage.
    """
    try:
        import libsql
    except ImportError:
        try:
            import libsql_experimental as libsql  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "TURSO_DATABASE_URL / TURSO_AUTH_TOKEN are set but no libSQL "
                "driver is installed. Add 'libsql' to requirements.txt and redeploy."
            ) from e
    # Passing the libsql:// URL positionally makes this a remote connection
    # (the driver detects the URL scheme); no local file is created.
    raw = libsql.connect(url, auth_token=token)
    return _TursoConnection(raw)


def get_connection():
    """
    Open and return a connection to the SQLite database.

    We set check_same_thread=False because Streamlit runs in a
    multi-threaded environment. SQLite handles this safely for a
    single-user application.

    We also enable foreign key enforcement — SQLite disables it
    by default, which would allow orphaned rows (e.g. transactions
    with no matching user). Enforcing it keeps the data consistent.

    If Turso credentials are configured, connections are routed to the hosted
    libSQL database (which persists across Streamlit Cloud restarts); otherwise
    a local SQLite file is used — unchanged behaviour for local dev and tests.
    """
    url, token = _turso_credentials()
    if url and token:
        return _connect_turso(url, token)

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
    Create all tables if they do not already exist, then run lightweight
    migrations that evolve the schema for databases created by older versions.

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

    # Migrations for pre-existing databases. CREATE TABLE IF NOT EXISTS will
    # not add columns to a table that already exists, so we add them here.
    _run_migrations(conn)
    conn.commit()
    conn.close()


def _run_migrations(conn) -> None:
    """
    Apply additive, idempotent schema migrations.

    SQLite's ALTER TABLE ADD COLUMN errors if the column already exists,
    so we first inspect the live schema with PRAGMA table_info and only
    add columns that are missing. This keeps every deployment — old or new —
    on the same schema without ever touching existing data.
    """
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}

    if "is_admin" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")

    if "last_login" not in existing:
        conn.execute("ALTER TABLE users ADD COLUMN last_login TEXT")


# ── 3. USER OPERATIONS ────────────────────────────────────────────────────────

# Usernames in this set are automatically granted admin rights on
# registration and login. Admin accounts can access the Admin Analytics
# Dashboard. To make your own account an admin, either:
#   (a) register/use one of these usernames, or
#   (b) add your username to this set, or
#   (c) call promote_to_admin("your_username") once.
# Lower-cased comparison, so "Admin" and "admin" are equivalent.
ADMIN_USERNAMES = {"admin", "yashkaria", "ykaria"}

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


def register_user(username: str, password: str, currency: str = "KES") -> tuple[bool, str]:
    """
    Create a new user account.

    Arguments:
        username: The chosen username (3–20 characters, letters/numbers/_ only)
        password: The chosen password (validated before this function is called)
        currency: The user's preferred currency code (e.g. "KES", "USD", "GBP")

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

    # Designated admin usernames are flagged at creation time.
    is_admin = 1 if username.lower() in ADMIN_USERNAMES else 0

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, currency, is_admin) VALUES (?, ?, ?, ?)",
            (username, password_hash_str, currency, is_admin),
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
            # Record activity (for active-user analytics) and ensure designated
            # admin usernames are flagged even if the account predates ADMIN_USERNAMES.
            now_str    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            make_admin = 1 if username.lower() in ADMIN_USERNAMES else row["is_admin"]
            conn.execute(
                "UPDATE users SET last_login = ?, is_admin = ? WHERE id = ?",
                (now_str, make_admin, row["id"]),
            )
            conn.commit()

            user = dict(row)
            user["last_login"] = now_str
            user["is_admin"]   = make_admin
            return True, user
        else:
            return False, None

    finally:
        conn.close()


def promote_to_admin(username: str) -> tuple[bool, str]:
    """
    Grant admin rights to an existing user by username.

    Provided as a convenience for designating an admin account without
    editing ADMIN_USERNAMES. Returns (success, message).
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE users SET is_admin = 1 WHERE username = ?", (username,)
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, f"No user named '{username}' found."
        return True, f"'{username}' is now an admin."
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


# ── 6. AGGREGATE / ANALYTICS OPERATIONS (anonymised) ──────────────────────────
# Every function in this section returns COHORT-LEVEL aggregates only.
# No usernames, passwords, or individual rows are ever returned — this is
# what allows the Admin Dashboard and School Impact Report to present real
# adoption and behavioural findings without exposing any individual's data.


def get_all_user_ids() -> list[int]:
    """Return every user id. Used to compute per-user economic scores in bulk."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id FROM users ORDER BY id").fetchall()
        return [row["id"] for row in rows]
    finally:
        conn.close()


def count_users() -> int:
    """Total number of registered users."""
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    finally:
        conn.close()


def count_active_users(days: int) -> int:
    """
    Number of distinct users active within the last `days`.

    A user is counted as active if they either logged in OR recorded a
    transaction inside the window. Combining both signals makes the metric
    robust even for accounts created before login tracking existed.
    """
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COUNT(DISTINCT uid) AS n FROM (
                SELECT id        AS uid FROM users
                    WHERE last_login IS NOT NULL AND last_login >= ?
                UNION
                SELECT user_id   AS uid FROM transactions
                    WHERE created_at >= ?
            )
            """,
            (cutoff, cutoff),
        ).fetchone()
        return row["n"]
    finally:
        conn.close()


def count_transactions() -> int:
    """Total number of transactions recorded across all users."""
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
    finally:
        conn.close()


def get_transaction_value_summary() -> dict:
    """
    Total monetary value analysed, split by type.

    Returns {"income": float, "expense": float, "total": float}.
    Note: values may mix currencies; the analytics layer reports the
    dominant currency alongside this figure for honest interpretation.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT type, COALESCE(SUM(amount),0) AS total FROM transactions GROUP BY type"
        ).fetchall()
        by_type = {row["type"]: row["total"] for row in rows}
        income  = by_type.get("income", 0.0)
        expense = by_type.get("expense", 0.0)
        return {"income": income, "expense": expense, "total": income + expense}
    finally:
        conn.close()


def get_category_totals() -> list[dict]:
    """
    Expense totals grouped by category across all users.
    Returns [{"category", "total", "count"}], largest first.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT   category,
                     COALESCE(SUM(amount),0) AS total,
                     COUNT(*)                AS count
            FROM     transactions
            WHERE    type = 'expense'
            GROUP BY category
            ORDER BY total DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_currency_distribution() -> list[dict]:
    """User counts grouped by preferred currency. Returns [{"currency","count"}]."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT currency, COUNT(*) AS count FROM users GROUP BY currency ORDER BY count DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_monthly_user_growth() -> list[dict]:
    """
    New registrations per calendar month, with a running cumulative total.
    Returns [{"month": "YYYY-MM", "new_users": int, "cumulative": int}].
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT   substr(created_at, 1, 7) AS month, COUNT(*) AS new_users
            FROM     users
            GROUP BY month
            ORDER BY month
            """
        ).fetchall()
        result, running = [], 0
        for row in rows:
            running += row["new_users"]
            result.append({
                "month": row["month"],
                "new_users": row["new_users"],
                "cumulative": running,
            })
        return result
    finally:
        conn.close()


def get_monthly_transaction_growth() -> list[dict]:
    """
    Transaction count and value per calendar month (by record creation date).
    Returns [{"month": "YYYY-MM", "count": int, "value": float}].
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT   substr(created_at, 1, 7)  AS month,
                     COUNT(*)                  AS count,
                     COALESCE(SUM(amount), 0)  AS value
            FROM     transactions
            GROUP BY month
            ORDER BY month
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# ── 7. ASSESSMENT OPERATIONS (anonymous research records) ─────────────────────
# One row per completed Financial Behaviour Assessment. Anonymous by default
# (user_id NULL). Only rows where the respondent consented are ever written —
# the consent check happens at the call site, so save_assessment is only
# invoked for opted-in respondents. Like section 6, the read functions return
# cohort-level aggregates only: no individual record is ever exposed in the UI.

# Columns written by save_assessment, in order. Centralised so the INSERT and
# any future column addition stay in lockstep.
_ASSESSMENT_COLUMNS = [
    "user_id", "source", "currency", "consent",
    "age_band", "life_stage", "gender",
    "ans_income", "ans_savings", "ans_commitment", "ans_buffer",
    "ans_timing", "ans_consistency", "ans_categories", "ans_inflation",
    "income_estimate", "savings_rate_pct", "commitment_rate_pct",
    "emergency_fund_months", "spending_cv", "bias_index",
    "health_score", "savings_score", "resilience_score",
    "consistency_score", "commitment_score", "present_bias_score",
    "present_bias_label",
]


def save_assessment(record: dict) -> int:
    """
    Persist one completed assessment and return its new row id.

    `record` is the dict produced by core.assessment.score_assessment().
    Any key not present defaults to NULL. This function performs NO scoring —
    it only stores what the assessment engine computed, keeping the data layer
    and the economics cleanly separated.
    """
    cols = ", ".join(_ASSESSMENT_COLUMNS)
    placeholders = ", ".join("?" * len(_ASSESSMENT_COLUMNS))
    values = [record.get(col) for col in _ASSESSMENT_COLUMNS]

    conn = get_connection()
    try:
        cur = conn.execute(
            f"INSERT INTO assessments ({cols}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def count_assessments() -> int:
    """Total number of completed (consented) assessment respondents."""
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) AS n FROM assessments").fetchone()["n"]
    finally:
        conn.close()


def count_anonymous_assessments() -> int:
    """
    Assessments not linked to a registered account (user_id IS NULL).

    Used to compute total unique participants without double-counting a
    respondent who later claims an account.
    """
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT COUNT(*) AS n FROM assessments WHERE user_id IS NULL"
        ).fetchone()["n"]
    finally:
        conn.close()


def get_assessment_scores() -> list[dict]:
    """
    Return per-respondent scores + demographics for cohort aggregation.

    Anonymised: no id, no timestamp, no link to identity — only the economic
    quantities and the aggregate-only demographic bands. This is the bridge
    that lets the analytics engine pool assessment respondents with tracking
    users on identical scoring.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT age_band, life_stage, gender,
                   savings_rate_pct, commitment_rate_pct, emergency_fund_months, bias_index,
                   health_score, savings_score, resilience_score,
                   consistency_score, commitment_score, present_bias_score,
                   present_bias_label, ans_categories
            FROM   assessments
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_assessment_growth() -> list[dict]:
    """
    Assessment completions per calendar month with a running cumulative total.
    Returns [{"month": "YYYY-MM", "completed": int, "cumulative": int}].
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT   substr(created_at, 1, 7) AS month, COUNT(*) AS completed
            FROM     assessments
            GROUP BY month
            ORDER BY month
            """
        ).fetchall()
        result, running = [], 0
        for row in rows:
            running += row["completed"]
            result.append({
                "month": row["month"],
                "completed": row["completed"],
                "cumulative": running,
            })
        return result
    finally:
        conn.close()
