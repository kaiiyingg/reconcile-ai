"""
Prediction routes: Generate and fetch ML predictions for transactions
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime

from app.domain.prediction import (
    PredictionListResponse,
    ForecastRequest
)
from app.dependencies.auth import get_current_user
from app.services import predictions as pred_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/generate")
async def generate_predictions(
    forecast: ForecastRequest,
    user=Depends(get_current_user)
):
    """
    Generate ML predictions for future transaction amounts.
    
    - **days_ahead**: Number of days to forecast (1-90)
    - **model_type**: Prediction model ('simple_average', 'moving_average', 'linear_trend')
    
    Returns predictions with confidence scores.
    """
    try:
        result = pred_service.generate_predictions(
            user_id=user["id"],
            days_ahead=forecast.days_ahead,
            model_type=forecast.model_type
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to generate predictions: {str(e)}")


@router.get("", response_model=PredictionListResponse)
async def get_predictions(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    start_date: Optional[datetime] = Query(None, description="Filter predictions after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter predictions before this date"),
    limit: int = Query(default=100, le=1000, description="Maximum predictions to return"),
    user=Depends(get_current_user)
):
    """
    Fetch all predictions for the authenticated user.
    
    Optional filters:
    - **model_type**: Filter by specific model
    - **start_date**: Show predictions after this date
    - **end_date**: Show predictions before this date
    - **limit**: Max results (default 100)
    """
    try:
        result = pred_service.fetch_predictions(
            user_id=user["id"],
            model_type=model_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return PredictionListResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch predictions: {str(e)}")


@router.get("/accuracy")
async def get_prediction_accuracy(
    model_type: Optional[str] = Query(None, description="Calculate accuracy for specific model"),
    user=Depends(get_current_user)
):
    """
    Get prediction accuracy metrics (MAE, RMSE, MAPE).
    
    Compares predictions vs actual values to measure model performance.
    Only includes predictions where actual values are available.
    """
    try:
        result = pred_service.get_prediction_accuracy(
            user_id=user["id"],
            model_type=model_type
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to calculate accuracy: {str(e)}")


@router.delete("/clear")
async def clear_predictions(
    model_type: Optional[str] = Query(None, description="Clear predictions for specific model only"),
    user=Depends(get_current_user)
):
    """
    Delete all predictions for the authenticated user.
    
    Optional: Specify model_type to only clear predictions from that model.
    """
    try:
        # Add this function to predictions service
        from app.db.connection import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if model_type:
            cursor.execute(
                "DELETE FROM predictions WHERE user_id = %s AND model_type = %s",
                (user["id"], model_type)
            )
        else:
            cursor.execute(
                "DELETE FROM predictions WHERE user_id = %s",
                (user["id"],)
            )
        
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Deleted {deleted_count} predictions",
            "deleted_count": deleted_count,
            "model_type": model_type
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to clear predictions: {str(e)}")
