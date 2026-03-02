CREATE TABLE IF NOT EXISTS anomalies (
    id TEXT PRIMARY KEY,                  -- Unique anomaly ID
    transaction_id TEXT NOT NULL,         -- Links to transaction
    anomaly_score REAL NOT NULL,          -- How unusual the transaction is
    flagged BOOLEAN DEFAULT 0,            -- High-risk flag
    explanation TEXT,                     -- Optional: SHAP / feature importance
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);