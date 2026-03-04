-- Predictions Table (Refactored)
-- Stores ML model predictions with improved schema design

CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL
        REFERENCES auth.users(id) ON DELETE CASCADE,
    model_type TEXT NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_value NUMERIC(15,2) NOT NULL,
    actual_value NUMERIC(15,2),
    confidence_score NUMERIC(5,4)
        CHECK (confidence_score BETWEEN 0 AND 1),
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Composite index for common queries (user + forecast date)
CREATE INDEX IF NOT EXISTS idx_predictions_user_forecast
    ON predictions(user_id, forecast_date DESC);

-- Additional performance indexes
CREATE INDEX IF NOT EXISTS idx_predictions_model_type
    ON predictions(model_type);