-- Anomalies Table (Refactored)
-- Stores detected anomalies with simplified lifecycle management

CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL
        REFERENCES auth.users(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL
        REFERENCES transactions(id) ON DELETE CASCADE,
    anomaly_score NUMERIC(5,4) NOT NULL
        CHECK (anomaly_score BETWEEN 0 AND 1),
    severity TEXT NOT NULL DEFAULT 'low'
        CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    reviewed BOOLEAN DEFAULT FALSE,
    explanation TEXT,
    shap_values JSONB,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user queries
CREATE INDEX IF NOT EXISTS idx_anomalies_user
    ON anomalies(user_id);

-- Index for transaction lookups
CREATE INDEX IF NOT EXISTS idx_anomalies_transaction
    ON anomalies(transaction_id);

-- Additional performance indexes
CREATE INDEX IF NOT EXISTS idx_anomalies_severity
    ON anomalies(severity);

CREATE INDEX IF NOT EXISTS idx_anomalies_reviewed
    ON anomalies(reviewed);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_anomalies_user_severity
    ON anomalies(user_id, severity);

CREATE INDEX IF NOT EXISTS idx_anomalies_user_unreviewed
    ON anomalies(user_id, reviewed) WHERE reviewed = FALSE;