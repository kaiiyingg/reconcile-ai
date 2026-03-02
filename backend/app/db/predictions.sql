CREATE TABLE IF NOT EXISTS predictions (
    id TEXT PRIMARY KEY,                  -- Unique ID or match transaction ID
    transaction_id TEXT NOT NULL,         -- Foreign key to transactions
    predicted_amount REAL NOT NULL,       -- Predicted value from ML model
    forecast_date DATETIME NOT NULL,      -- For multi-step prediction
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);