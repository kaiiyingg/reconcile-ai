CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL
        REFERENCES auth.users(id) ON DELETE CASCADE,
    transaction_date TIMESTAMPTZ NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount <> 0),
    category TEXT NOT NULL,
    description TEXT,
    source TEXT NOT NULL DEFAULT 'uploaded'
        CHECK (source IN ('uploaded', 'generated')),
    status TEXT NOT NULL DEFAULT 'completed'
        CHECK (status IN ('completed', 'reconciled', 'flagged')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Composite index for common queries (user + date)
CREATE INDEX IF NOT EXISTS idx_transactions_user_date
    ON transactions(user_id, transaction_date DESC);

-- Additional performance indexes
CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions(category);

CREATE INDEX IF NOT EXISTS idx_transactions_status
    ON transactions(status);

CREATE INDEX IF NOT EXISTS idx_transactions_user_category
    ON transactions(user_id, category);

CREATE INDEX IF NOT EXISTS idx_transactions_user_status
    ON transactions(user_id, status);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();