"""
ReconcileAI Backend - FastAPI Application
Main entry point for the API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth

# =====================================================
# CREATE FASTAPI APP
# =====================================================

app = FastAPI(
    title="ReconcileAI API",
    description="AI-powered transaction reconciliation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =====================================================
# CORS MIDDLEWARE
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# INCLUDE ROUTERS
# =====================================================

app.include_router(auth.router)

# =====================================================
# ROOT ENDPOINT
# =====================================================

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


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )
