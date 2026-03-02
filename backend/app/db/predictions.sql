-- =====================================================
-- PREDICTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    model_type TEXT NOT NULL,  -- 'gradient_boosting', 'arima', 'lstm'
    predicted_amount DECIMAL(15, 2) NOT NULL,
    actual_amount DECIMAL(15, 2),
    confidence_score DECIMAL(5, 4),  -- 0.0000 to 1.0000
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    forecast_date TIMESTAMP WITH TIME ZONE NOT NULL,  -- When prediction is for
    accuracy DECIMAL(5, 2),  -- Percentage accuracy after actual known
    model_version TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_transaction_id ON predictions(transaction_id);

-- Query optimization indexes
CREATE INDEX IF NOT EXISTS idx_predictions_model_type ON predictions(model_type);
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_date ON predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_predictions_forecast_date ON predictions(forecast_date);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_predictions_user_date ON predictions(user_id, prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_user_model ON predictions(user_id, model_type);
CREATE INDEX IF NOT EXISTS idx_predictions_user_forecast ON predictions(user_id, forecast_date DESC);