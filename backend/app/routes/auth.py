"""
Supabase authentication routes: register and login with email/password
"""
from fastapi import APIRouter, HTTPException, status
from app.domain.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    LoginResponse,
    MessageResponse
)
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register with email and password using Supabase Auth"""
    try:
        supabase = get_supabase_client()
        
        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        return LoginResponse(
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                created_at=str(response.user.created_at)
            ),
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """Login with email and password using Supabase Auth"""
    try:
        supabase = get_supabase_client()
        
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return LoginResponse(
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                created_at=str(response.user.created_at)
            ),
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout (client discards tokens)"""
    return MessageResponse(message="Logged out successfully")
