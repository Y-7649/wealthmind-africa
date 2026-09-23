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

-- ============================================================
-- ASSESSMENTS
-- One honest record per completed Financial Behaviour Assessment.
--
-- WealthMind's research backbone: a behavioural economics assessment
-- studying financial decision-making across different age groups and
-- life stages. Each row is one anonymous respondent (user_id is NULL
-- unless they later claim an account).
--
-- NO synthetic transactions are ever created. The assessment maps a
-- respondent's self-reported answers to the SAME intermediate quantities
-- the tracker derives from transactions, then applies the SAME scoring
-- functions (core/health_score, core/present_bias). One source of truth.
--
-- Only rows where consent = 'yes' are ever written — if a respondent
-- declines, their results are shown but nothing is saved.
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at            TEXT    NOT NULL DEFAULT (DATETIME('now')),
    user_id               INTEGER REFERENCES users(id),   -- NULL = anonymous
    source                TEXT    NOT NULL DEFAULT 'assessment',  -- assessment | tracker | imported
    currency              TEXT    NOT NULL DEFAULT 'KES',
    consent               TEXT    NOT NULL DEFAULT 'yes',  -- only 'yes' rows are stored

    -- Demographics (aggregate-only; never displayed individually)
    age_band              TEXT,
    life_stage            TEXT,
    gender                TEXT,

    -- Raw answer codes — auditable, and allow recomputation if a curve changes
    ans_income            TEXT,
    ans_savings           TEXT,
    ans_commitment        TEXT,
    ans_buffer            TEXT,
    ans_timing            TEXT,
    ans_consistency       TEXT,
    ans_categories        TEXT,   -- two category codes, comma-joined
    ans_inflation         TEXT,

    -- Derived engine inputs (unit-free except income_estimate)
    income_estimate       REAL,
    savings_rate_pct      REAL,
    commitment_rate_pct   REAL,
    emergency_fund_months REAL,
    spending_cv           REAL,
    bias_index            REAL,

    -- Final scores (produced by the SHARED scoring functions)
    health_score          REAL,
    savings_score         REAL,
    resilience_score      REAL,
    consistency_score     REAL,
    commitment_score      REAL,
    present_bias_score    REAL,
    present_bias_label    TEXT
);

CREATE INDEX IF NOT EXISTS idx_assessments_created
    ON assessments(created_at);

-- ============================================================
-- REPORT_REQUESTS  (data domain C — optional contact / email)
-- Optional email capture for participants who want a personalised report.
-- Contact data is stored SEPARATELY from the financial responses: the email
-- lives here, the financial answers live in the assessments table. The two are
-- connected only by the internal assessment_id below (never merged into one
-- row, and no email column is ever added to assessments). This is separation,
-- not absolute anonymity: assessment_id is an internal link an administrator
-- could in principle follow, so participant-facing wording says 'stored
-- separately', never 'can never be linked'. Only written when a participant
-- opts in AFTER seeing their results (email is never required to finish).
-- (No semicolons in these comments — the libSQL adapter splits on semicolons.)
-- ============================================================
CREATE TABLE IF NOT EXISTS report_requests (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at         TEXT    NOT NULL DEFAULT (DATETIME('now')),
    -- Internal link to the financial responses. Email lives here, the financial
    -- answers live in assessments — connected only by this id, never merged.
    assessment_id      INTEGER REFERENCES assessments(id),
    email              TEXT    NOT NULL,
    health_score       REAL,
    present_bias_score REAL,
    resilience_score   REAL,
    savings_score      REAL,
    present_bias_label TEXT,
    sent               INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_report_requests_created
    ON report_requests(created_at);

-- ============================================================
-- V11_EXPERIMENTS  (data domain B — Version 1.1 experimental)
-- Responses to the OPTIONAL Version 1.1 behavioural-finance mini-experiment.
-- Kept in its own table, completely separate from the Version 1.0 assessments
-- table, so it is impossible for these answers to leak into the original
-- research instrument. Nothing here feeds the Financial Health, Present Bias,
-- Savings, Consistency or Resilience scores — this is exploratory data only.
-- Anonymous: no email, no name, no user link. Written only on submit.
-- (No semicolons in these comments — the libSQL adapter splits on semicolons.)
-- ============================================================
CREATE TABLE IF NOT EXISTS v11_experiments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at        TEXT    NOT NULL DEFAULT (DATETIME('now')),
    module_version    TEXT    NOT NULL DEFAULT '1.1',
    scenario_set      TEXT    NOT NULL DEFAULT 'core3',

    -- Raw answer codes — one per scenario. Meaning documented in
    -- pages/11_experiments.py. Never scored, only aggregated.
    ans_time_pref     TEXT,   -- immediate vs delayed reward
    ans_windfall      TEXT,   -- windfall allocation (spend/save/invest/split)
    ans_real_nominal  TEXT    -- nominal vs real wealth understanding
);

CREATE INDEX IF NOT EXISTS idx_v11_experiments_created
    ON v11_experiments(created_at);
