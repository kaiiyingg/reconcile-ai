"""
Transaction models and schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class TransactionCreate(BaseModel):
    transaction_date: datetime
    amount: Decimal
    category: str
    description: Optional[str] = None
    source: str = "manual"


class TransactionUpdate(BaseModel):
    transaction_date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    transaction_date: datetime
    amount: Decimal
    category: str
    description: Optional[str]
    source: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    transactions: List[TransactionResponse]


class CSVUploadResponse(BaseModel):
    message: str
    uploaded_count: int
    failed_count: int
    errors: Optional[List[str]] = None
