"""
Anomaly models and schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid


class AnomalyCreate(BaseModel):
    transaction_id: uuid.UUID
    anomaly_score: Decimal
    severity: str = "low"
    explanation: Optional[str] = None
    shap_values: Optional[Dict[str, Any]] = None


class AnomalyUpdate(BaseModel):
    reviewed: Optional[bool] = None
    explanation: Optional[str] = None


class AnomalyResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    transaction_id: uuid.UUID
    anomaly_score: Decimal
    severity: str
    reviewed: bool
    explanation: Optional[str]
    shap_values: Optional[Dict[str, Any]]
    detected_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    total: int
    anomalies: List[AnomalyResponse]


class AnomalyStatsResponse(BaseModel):
    total_anomalies: int
    flagged_count: int
    unreviewed_count: int
    severity_breakdown: Dict[str, int]
    recent_anomalies: List[AnomalyResponse]
