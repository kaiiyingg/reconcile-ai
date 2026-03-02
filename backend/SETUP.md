# Backend Setup Guide

## 📦 Install Dependencies

Run this command in the backend directory:

```bash
cd backend
pip install -r requirements.txt
```

**Note:** Use `-r` flag to install from requirements.txt file!

## 🔧 Environment Setup

Make sure your `.env` file exists with:

```
# Database (Supabase)
user=postgres
password=Oreoicecream$88
host=db.wgdkjdvmaqfbxzxvjnkq.supabase.co
port=5432
dbname=postgres

# JWT Secret (change in production!)
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## 🗄️ Database Setup

Run the SQL files in order to create tables:

```sql
-- In Supabase SQL Editor or psql:
\i app/db/users.sql
\i app/db/transactions.sql
\i app/db/predictions.sql
\i app/db/anomalies.sql
```

Or use the setup script:

```bash
python app/db/setup_database.py
```

## 🚀 Run the Server

```bash
# From backend directory
python app/main.py

# Or using uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will run on: http://localhost:8000

## 📚 API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Authentication Endpoints

### Register

```
POST /api/auth/register
Body: {
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

### Login

```
POST /api/auth/login
Body: {
  "email": "user@example.com",
  "password": "password123"
}
```

### Get Current User

```
GET /api/auth/me
Headers: {
  "Authorization": "Bearer <access_token>"
}
```

### Refresh Token

```
POST /api/auth/refresh
Body: {
  "refresh_token": "<refresh_token>"
}
```

### Logout

```
POST /api/auth/logout
Headers: {
  "Authorization": "Bearer <access_token>"
}
```

## 📦 Installed Packages

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **PyJWT** - JWT tokens
- **passlib** - Password hashing
- **psycopg2-binary** - PostgreSQL driver
- **python-dotenv** - Environment variables
- **pandas, numpy, scikit-learn** - Data/ML

## 🐛 Troubleshooting

**Error: Import "fastapi" could not be resolved**

- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt` again

**Error: No module named 'app'**

- Run server from backend directory
- Or use: `python -m app.main`

**Database connection error**

- Check .env file credentials
- Verify Supabase is accessible
