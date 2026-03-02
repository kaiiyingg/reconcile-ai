"""
ReconcileAI Backend - FastAPI Application
Main entry point for the API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, transactions, predictions, anomalies, insights, reports, websocket

app = FastAPI(
    title="ReconcileAI API",
    description="AI-powered transaction reconciliation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(predictions.router)
app.include_router(anomalies.router)
app.include_router(insights.router)
app.include_router(reports.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to ReconcileAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ReconcileAI API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )
