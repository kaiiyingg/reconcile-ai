"""
Simple authentication routes: register and login with password matching only
"""
from fastapi import APIRouter, HTTPException, status
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

from app.models.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    LoginResponse,
    MessageResponse
)
from app.utils.auth import verify_password
from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user - stores password as plain text for simple matching"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (user_data.username,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Store password directly (simple matching - NOT secure for production!)
        user_id = uuid.uuid4()
        cursor.execute(
            """
            INSERT INTO users (id, username, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, created_at
            """,
            (user_id, user_data.username, user_data.password)
        )
        
        new_user = cursor.fetchone()
        conn.commit()
        
        return LoginResponse(
            user=UserResponse(**new_user),
            success=True
        )
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """Login with username and password - simple matching"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """
            SELECT id, username, password_hash, created_at
            FROM users WHERE username = %s
            """,
            (credentials.username,)
        )
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Simple password matching
        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user['id'],)
        )
        conn.commit()
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return LoginResponse(
            user=UserResponse(**user_data),
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout - just returns success (no server-side session to clear)"""
    return MessageResponse(
        message="Logged out successfully",
        success=True
    )