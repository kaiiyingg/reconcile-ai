"""
Extracts and validates JWT token from request headers
Returns the authenticated user's information
"""
from fastapi import HTTPException, Header, Depends
from typing import Optional
import os
from dotenv import load_dotenv

from app.supabase_client import get_supabase_client

load_dotenv()


async def get_current_user(
    authorization: Optional[str] = Header(None)
):
    
    # Check if Authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header. Please login."
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme. Use 'Bearer <token>'"
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
    
    # Validate token with Supabase
    try:
        supabase = get_supabase_client()
        
        # Get user from JWT token
        # Supabase automatically validates the token
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token. Please login again."
            )
        
        user = user_response.user
        
        # Return user information as a dict
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "email_confirmed_at": user.email_confirmed_at,
            # Add other user fields as needed
        }
        
    except HTTPException:
        # Re-raise our custom HTTPExceptions
        raise
    except Exception as e:
        # Handle any other errors (network issues, invalid token format, etc.)
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )
