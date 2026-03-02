"""
Prediction models and schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class PredictionCreate(BaseModel):
    transaction_id: Optional[uuid.UUID] = None
    model_type: str
    predicted_amount: Decimal
    forecast_date: datetime
    confidence_score: Optional[Decimal] = None
    forecast_horizon: Optional[int] = None


class PredictionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    transaction_id: Optional[uuid.UUID]
    model_type: str
    predicted_amount: Decimal
    actual_amount: Optional[Decimal]
    confidence_score: Optional[Decimal]
    prediction_date: datetime
    forecast_date: datetime
    accuracy: Optional[Decimal]
    model_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    total: int
    predictions: List[PredictionResponse]


class ForecastRequest(BaseModel):
    days_ahead: int = Field(default=7, ge=1, le=90)
    model_type: str = "gradient_boosting"


class ForecastResponse(BaseModel):
    forecast_date: datetime
    predicted_amount: Decimal
    confidence_score: Decimal
    model_type: str
