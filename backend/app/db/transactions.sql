CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,           -- Use UUID stored as text
    timestamp DATETIME NOT NULL,   -- When transaction occurred
    amount REAL NOT NULL,          -- Transaction amount
    category TEXT NOT NULL,        -- Transaction type/category
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- When uploaded to system
);
