## Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs on:** http://localhost:8000

## Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend runs on:** http://localhost:8080