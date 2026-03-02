"""
Authentication models and schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    full_name: str
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    company_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True
