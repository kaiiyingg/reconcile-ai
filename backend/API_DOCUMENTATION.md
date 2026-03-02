# 📚 ReconcileAI API Documentation

## Base URL

`http://localhost:8000`

---

## 🔐 Authentication Endpoints

### Register User

```
POST /api/auth/register
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "company_name": "Acme Corp"
}
```

### Login

```
POST /api/auth/login
```

**Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Get Current User

```
GET /api/auth/me
Headers: Authorization: Bearer <token>
```

---

## 💰 Transaction Endpoints

### Upload CSV/Excel

```
POST /api/transactions/upload
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: transactions.csv
```

### Generate Demo Data

```
POST /api/transactions/generate-demo?count=100
Headers: Authorization: Bearer <token>
```

### Get All Transactions

```
GET /api/transactions?start_date=2024-01-01&end_date=2024-12-31&category=Revenue&limit=100&offset=0
Headers: Authorization: Bearer <token>
```

### Get Single Transaction

```
GET /api/transactions/{transaction_id}
Headers: Authorization: Bearer <token>
```

---

## 🔮 Prediction Endpoints

### Run Predictions

```
POST /api/predictions/run
Headers: Authorization: Bearer <token>

Body:
{
  "days_ahead": 7,
  "model_type": "gradient_boosting"
}
```

### Get Predictions

```
GET /api/predictions?start_date=2024-01-01&model_type=gradient_boosting&limit=100
Headers: Authorization: Bearer <token>
```

### Get Forecast

```
GET /api/predictions/forecast?days=30
Headers: Authorization: Bearer <token>
```

---

## ⚠️ Anomaly Endpoints

### Run Anomaly Detection

```
POST /api/anomalies/run?threshold=0.75
Headers: Authorization: Bearer <token>
```

### Get Anomalies

```
GET /api/anomalies?severity=high&flagged=true&reviewed=false&limit=100
Headers: Authorization: Bearer <token>
```

### Update Anomaly

```
PATCH /api/anomalies/{anomaly_id}
Headers: Authorization: Bearer <token>

Body:
{
  "reviewed": true,
  "resolution_notes": "False positive - approved transaction"
}
```

### Get Anomaly Stats

```
GET /api/anomalies/stats
Headers: Authorization: Bearer <token>
```

---

## 💡 Insights Endpoint

### Get Actionable Insights

```
GET /api/insights
Headers: Authorization: Bearer <token>
```

**Returns:**

```json
[
  {
    "type": "critical",
    "title": "Critical Anomalies Detected",
    "message": "5 critical anomalies require immediate review",
    "confidence": 0.95,
    "action": "Review anomalies in the Anomalies tab",
    "icon": "alert-triangle"
  }
]
```

---

## 📊 Reports Endpoints

### Generate CSV Report

```
GET /api/reports/csv?report_type=transactions&start_date=2024-01-01&end_date=2024-12-31
Headers: Authorization: Bearer <token>
```

**Report Types:**

- `transactions` - All transactions
- `predictions` - All predictions
- `anomalies` - All anomalies
- `full` - Complete report

### Get Report Summary

```
GET /api/reports/summary
Headers: Authorization: Bearer <token>
```

---

## 🔌 WebSocket Endpoints

### Transaction Updates

```
WS ws://localhost:8000/ws/transactions
```

### Anomaly Updates

```
WS ws://localhost:8000/ws/anomalies
```

### Prediction Updates

```
WS ws://localhost:8000/ws/predictions
```

**WebSocket Message Format:**

```json
{
  "type": "new_transaction",
  "data": {
    "id": "...",
    "amount": 1500.0,
    "category": "Revenue"
  }
}
```

---

## 📋 Common Query Parameters

### Pagination

- `limit` (default: 100, max: 1000)
- `offset` (default: 0)

### Date Filters

- `start_date` (ISO format: 2024-01-01)
- `end_date` (ISO format: 2024-12-31)

### Transaction Filters

- `category` (Revenue, Expense, etc.)
- `status` (pending, completed, reconciled)

### Anomaly Filters

- `severity` (low, medium, high, critical)
- `flagged` (true/false)
- `reviewed` (true/false)

---

## 🎯 Complete Workflow Example

### 1. User Registration & Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Generate Demo Data

```bash
curl -X POST http://localhost:8000/api/transactions/generate-demo?count=100 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Run Predictions

```bash
curl -X POST http://localhost:8000/api/predictions/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days_ahead":30,"model_type":"gradient_boosting"}'
```

### 4. Run Anomaly Detection

```bash
curl -X POST http://localhost:8000/api/anomalies/run?threshold=0.75 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Insights

```bash
curl -X GET http://localhost:8000/api/insights \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Download Report

```bash
curl -X GET "http://localhost:8000/api/reports/csv?report_type=full" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.csv
```

---

## 🚀 Quick Test

Visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI)

---

## ✅ All Routes Implemented

- ✅ Authentication (register, login, logout, me)
- ✅ Transactions (upload CSV, generate demo, get all)
- ✅ Predictions (run models, get forecasts)
- ✅ Anomalies (detect, review, stats)
- ✅ Insights (actionable suggestions)
- ✅ Reports (CSV export, summary)
- ✅ WebSocket (real-time updates)
