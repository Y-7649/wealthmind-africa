-- WealthMind Africa
-- Database Schema
-- SQLite

-- ============================================================
-- USERS
-- Stores authentication credentials.
-- Passwords are stored as bcrypt hashes — never plaintext.
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    currency      TEXT    NOT NULL DEFAULT 'KES',
    created_at    TEXT    NOT NULL DEFAULT (DATE('now')),
    -- is_admin gates the Admin Analytics Dashboard. 0 = normal user, 1 = admin.
    is_admin      INTEGER NOT NULL DEFAULT 0,
    -- last_login records the most recent successful login (DATETIME).
    -- Used to compute active-user counts for the impact analytics.
    last_login    TEXT
);

-- ============================================================
-- TRANSACTIONS
-- Every income and expense entry made by a user.
-- 'type' is strictly 'income' or 'expense'.
-- 'category' uses a controlled vocabulary enforced
-- at the application layer to ensure data is
-- analytically tractable across all four modules.
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    date        TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    category    TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK(amount > 0),
    description TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (DATETIME('now'))
);

-- Index for fast per-user lookups — every query filters by user_id
CREATE INDEX IF NOT EXISTS idx_transactions_user
    ON transactions(user_id);

-- Index for date-range queries used in monthly summaries
-- and the Kenya Inflation Context module
CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(user_id, date);

-- ============================================================
-- HEALTH_SNAPSHOTS
-- Stores the computed Financial Health Score each time
-- the user visits the Health Score page.
-- Preserving history allows the score to be plotted
-- as a trend line — showing financial progress over time.
-- ============================================================
CREATE TABLE IF NOT EXISTS health_snapshots (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL REFERENCES users(id),
    snapshot_date           TEXT    NOT NULL DEFAULT (DATE('now')),
    overall_score           REAL,
    savings_rate_score      REAL,
    emergency_fund_score    REAL,
    consistency_score       REAL,
    commitment_score        REAL,
    savings_rate_pct        REAL,
    emergency_fund_months   REAL,
    spending_cv             REAL,
    commitment_rate_pct     REAL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user
    ON health_snapshots(user_id, snapshot_date);

-- ============================================================
-- GOALS
-- Reserved for future expansion.
-- Allows users to define savings targets with deadlines.
-- Not used in the MVP but included so the database
-- does not need to be restructured later.
-- ============================================================
CREATE TABLE IF NOT EXISTS goals (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES users(id),
    name           TEXT    NOT NULL,
    target_amount  REAL    NOT NULL CHECK(target_amount > 0),
    saved_amount   REAL    NOT NULL DEFAULT 0,
    target_date    TEXT,
    category       TEXT    DEFAULT 'general',
    created_at     TEXT    NOT NULL DEFAULT (DATE('now'))
);

CREATE INDEX IF NOT EXISTS idx_goals_user
    ON goals(user_id);
