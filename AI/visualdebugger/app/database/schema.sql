-- ============================================================
--  CNN Visual Debugger — SQLite Schema
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE,
    email         TEXT     NOT NULL UNIQUE,
    password_hash TEXT     NOT NULL,
    role          TEXT     NOT NULL DEFAULT 'user',   -- 'user' | 'admin'
    avatar_url    TEXT,
    bio           TEXT,
    is_active     INTEGER  NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Test Sessions ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS test_sessions (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_name  TEXT,
    target_url    TEXT     NOT NULL,
    status        TEXT     NOT NULL DEFAULT 'pending',  -- pending|running|completed|failed
    bugs_found    INTEGER  NOT NULL DEFAULT 0,
    accuracy      REAL,
    start_time    DATETIME,
    end_time      DATETIME,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Screenshots ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS screenshots (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    session_id    INTEGER  NOT NULL REFERENCES test_sessions(id) ON DELETE CASCADE,
    file_path     TEXT     NOT NULL,
    width         INTEGER,
    height        INTEGER,
    captured_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Bug Reports ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bug_reports (
    id               INTEGER  PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER  NOT NULL REFERENCES test_sessions(id) ON DELETE CASCADE,
    screenshot_id    INTEGER  REFERENCES screenshots(id),
    bug_type         TEXT     NOT NULL,   -- layout|color|overlap|missing|alignment|contrast
    severity         TEXT     NOT NULL DEFAULT 'medium',  -- low|medium|high|critical
    confidence       REAL     NOT NULL,
    bounding_box     TEXT,                -- JSON: {"x":0,"y":0,"w":100,"h":50}
    screenshot_path  TEXT,
    heatmap_path     TEXT,
    description      TEXT,
    is_false_positive INTEGER NOT NULL DEFAULT 0,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Model Metrics ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS model_metrics (
    id           INTEGER  PRIMARY KEY AUTOINCREMENT,
    epoch        INTEGER  NOT NULL,
    train_acc    REAL     NOT NULL,
    val_acc      REAL     NOT NULL,
    train_loss   REAL     NOT NULL,
    val_loss     REAL     NOT NULL,
    precision    REAL,
    recall       REAL,
    f1_score     REAL,
    recorded_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Contact Messages ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    name       TEXT     NOT NULL,
    email      TEXT     NOT NULL,
    subject    TEXT,
    message    TEXT     NOT NULL,
    is_read    INTEGER  NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_sessions_user    ON test_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status  ON test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_bugs_session     ON bug_reports(session_id);
CREATE INDEX IF NOT EXISTS idx_bugs_type        ON bug_reports(bug_type);
CREATE INDEX IF NOT EXISTS idx_bugs_severity    ON bug_reports(severity);
CREATE INDEX IF NOT EXISTS idx_screenshots_sess ON screenshots(session_id);
