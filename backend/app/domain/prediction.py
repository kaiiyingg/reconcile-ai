"""
Prediction models and schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class PredictionCreate(BaseModel):
    model_type: str
    forecast_date: datetime
    predicted_value: Decimal
    actual_value: Optional[Decimal] = None
    confidence_score: Optional[Decimal] = None
    model_version: Optional[str] = None


class PredictionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    model_type: str
    forecast_date: datetime
    predicted_value: Decimal
    actual_value: Optional[Decimal]
    confidence_score: Optional[Decimal]
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
    predicted_value: Decimal
    confidence_score: Decimal
    model_type: str
