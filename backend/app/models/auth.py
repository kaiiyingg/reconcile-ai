"""
Authentication models and schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    username: str
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserResponse
    success: bool = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True
