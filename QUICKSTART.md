# 🚀 Quick Start Guide

## Start Backend

```bash
cd backend
source venv/bin/activate
python app/main.py
```

**Backend runs on:** http://localhost:8000

## Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend runs on:** http://localhost:8080

## Access App

Open browser: **http://localhost:8080**

---

## First Time Setup

### 1. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Create Database Tables

Run these SQL files in Supabase SQL Editor:

- `backend/app/db/users.sql`
- `backend/app/db/transactions.sql`
- `backend/app/db/predictions.sql`
- `backend/app/db/anomalies.sql`

---

## Test Connection

```bash
chmod +x test-connection.sh
./test-connection.sh
```

---

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Default Credentials (After Registration)

Create your own account at: http://localhost:8080/register

---

For detailed setup instructions, see [STARTUP_GUIDE.md](./STARTUP_GUIDE.md)
