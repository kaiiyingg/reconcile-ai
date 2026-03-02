CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    anomaly_score DECIMAL(5, 4) NOT NULL,  -- 0.0000 to 1.0000
    severity TEXT DEFAULT 'low',  -- 'low', 'medium', 'high', 'critical'
    flagged BOOLEAN DEFAULT FALSE,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    explanation TEXT,  -- SHAP values / feature importance
    shap_values JSONB,  -- Detailed SHAP explanations
    resolution_notes TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_anomalies_user_id ON anomalies(user_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_transaction_id ON anomalies(transaction_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_reviewed_by ON anomalies(reviewed_by);

-- Query optimization indexes
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_flagged ON anomalies(flagged);
CREATE INDEX IF NOT EXISTS idx_anomalies_reviewed ON anomalies(reviewed);
CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at ON anomalies(detected_at);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_anomalies_user_severity ON anomalies(user_id, severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_user_flagged ON anomalies(user_id, flagged);
CREATE INDEX IF NOT EXISTS idx_anomalies_user_unreviewed ON anomalies(user_id, reviewed) WHERE reviewed = FALSE;
CREATE INDEX IF NOT EXISTS idx_anomalies_user_detected ON anomalies(user_id, detected_at DESC);