"""
Prediction routes: run prediction models, fetch predictions
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import random
import uuid
from decimal import Decimal

from app.domain.prediction import (
    PredictionResponse,
    PredictionListResponse,
    ForecastRequest,
    ForecastResponse
)
from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/run")
async def run_predictions(
    forecast: ForecastRequest,
    user_id: str = Header(..., alias="x-user-id")
):
    """Run prediction models for specified forecast horizon"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """
            SELECT id, timestamp, amount, category
            FROM transactions
            WHERE user_id = %s AND status = 'completed'
            ORDER BY timestamp DESC
            LIMIT 100
            """,
            (user_id,)
        )
        transactions = cursor.fetchall()
        
        if len(transactions) < 10:
            raise HTTPException(
                status_code=400,
                detail="Need at least 10 transactions to generate predictions"
            )
        
        avg_amount = sum(float(t['amount']) for t in transactions) / len(transactions)
        
        predictions_created = 0
        
        for day in range(1, forecast.days_ahead + 1):
            forecast_date = datetime.now() + timedelta(days=day)
            
            variation = random.uniform(0.8, 1.2)
            predicted_amount = avg_amount * variation
            confidence = random.uniform(0.75, 0.95)
            
            cursor.execute(
                """
                INSERT INTO predictions 
                (id, user_id, model_type, predicted_amount, confidence_score, forecast_date, model_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    uuid.uuid4(),
                    user_id,
                    forecast.model_type,
                    round(predicted_amount, 2),
                    round(confidence, 4),
                    forecast_date,
                    "v1.0"
                )
            )
            predictions_created += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Generated {predictions_created} predictions",
            "model_type": forecast.model_type,
            "days_ahead": forecast.days_ahead,
            "predictions_count": predictions_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("", response_model=PredictionListResponse)
async def get_predictions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    model_type: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Header(..., alias="x-user-id")
):
    """Fetch predictions with optional filters"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM predictions WHERE user_id = %s"
        params = [user_id]
        
        if start_date:
            query += " AND forecast_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND forecast_date <= %s"
            params.append(end_date)
        
        if model_type:
            query += " AND model_type = %s"
            params.append(model_type)
        
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        query += " ORDER BY forecast_date ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        predictions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return PredictionListResponse(
            total=total,
            predictions=[PredictionResponse(**p) for p in predictions]
        )
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch predictions: {str(e)}")


@router.get("/forecast", response_model=List[ForecastResponse])
async def get_forecast(
    days: int = Query(default=7, ge=1, le=90),
    user_id: str = Header(..., alias="x-user-id")
):
    """Get forecast for next N days"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        end_date = datetime.now() + timedelta(days=days)
        
        cursor.execute(
            """
            SELECT forecast_date, predicted_amount, confidence_score, model_type
            FROM predictions
            WHERE user_id = %s 
            AND forecast_date >= NOW()
            AND forecast_date <= %s
            ORDER BY forecast_date ASC
            """,
            (user_id, end_date)
        )
        forecasts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [ForecastResponse(**f) for f in forecasts]
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast: {str(e)}")
