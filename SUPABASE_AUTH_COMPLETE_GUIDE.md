# 🔐 Supabase Auth Integration Guide

## ✅ What You Get with Supabase Auth

- **Email/Password authentication** (managed by Supabase)
- **JWT tokens** (secure, auto-expiring)
- **Row Level Security (RLS)** (users only see their own data)
- **No custom users table needed** (Supabase manages `auth.users`)
- **Production-ready security**

---

## 📋 Setup Steps

### Step 1: Enable Auth in Supabase Dashboard (DONE IN DASHBOARD)

1. Go to https://supabase.com/dashboard
2. Click **Authentication** → **Providers**
3. Enable **Email** provider
4. **Disable** "Confirm email" (for development)
5. Click **Save**

### Step 2: Run Migration (DONE IN SQL EDITOR)

Copy and paste this entire migration into **Supabase SQL Editor**:

```sql
${await read_file('/Users/kaiying/Downloads/reconcile-ai/reconcile-ai/backend/app/db/migrate_to_supabase_auth.sql')}
```

### Step 3: Get Supabase Credentials

From Supabase Dashboard:

1. Click **Project Settings** (gear icon)
2. Click **API**
3. Copy these values:

- **Project URL**: `https://xxxxx.supabase.co`
- **anon public key**: `eyJhbGciOiJIUzI1...` (long string)

---

## 🔧 Backend Setup

### 1. Update `.env` file

Add these to `/backend/.env`:

```env
# Existing database config (keep these)
user=postgres
password=Oreoicecream$88
host=db.wgdkjdvmaqfbxzxvjnkq.supabase.co
port=5432
dbname=postgres

# NEW: Supabase Auth credentials
SUPABASE_URL=https://wgdkjdvmaqfbxzxvjnkq.supabase.co
SUPABASE_KEY=your_anon_public_key_here
```

### 2. Install Supabase Python Client

```bash
cd backend
pip3 install supabase==2.3.0
```

### 3. Create Supabase Client Helper

Create `/backend/app/supabase_client.py`:

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Returns the Supabase client instance"""
    return supabase
```

### 4. Update Auth Models

Replace `/backend/app/models/auth.py`:

```python
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str

class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

class MessageResponse(BaseModel):
    message: str
```

### 5. Update Auth Routes

Replace `/backend/app/routes/auth.py`:

```python
from fastapi import APIRouter, HTTPException, status
from app.models.auth import UserRegister, UserLogin, LoginResponse, MessageResponse, UserResponse
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=LoginResponse)
async def register(credentials: UserRegister):
    """Register with email and password"""
    try:
        supabase = get_supabase_client()

        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
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
                created_at=response.user.created_at
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
    """Login with email and password"""
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
                created_at=response.user.created_at
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
```

### 6. Create Auth Dependency for Protected Routes

Create `/backend/app/dependencies.py`:

```python
from fastapi import Header, HTTPException, status
from app.supabase_client import get_supabase_client

async def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.replace("Bearer ", "")

    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)

        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return user.user.id

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

### 7. Update Transaction Routes

Replace the header approach with proper auth:

```python
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_id

@router.post("/generate-demo")
async def generate_demo_transactions(
    count: int = Query(default=100, ge=10, le=1000),
    user_id: str = Depends(get_current_user_id)  # ✅ Secure!
):
    """Generate demo data for logged-in user"""
    # user_id is automatically extracted from JWT token
    # ...
```

---

## 🎨 Frontend Setup

### 1. Install Supabase JS Client

```bash
cd frontend
npm install @supabase/supabase-js
```

### 2. Create Supabase Client

Create `/frontend/src/lib/supabase.ts`:

```typescript
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://wgdkjdvmaqfbxzxvjnkq.supabase.co";
const supabaseAnonKey = "your_anon_public_key_here";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### 3. Update Auth Context

Replace `/frontend/src/contexts/AuthContext.tsx`:

```typescript
import { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { User } from '@supabase/supabase-js'

interface AuthContextType {
  user: User | null
  session: any
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setIsLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const register = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) throw error
    setUser(data.user)
    setSession(data.session)
  }

  const login = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    setUser(data.user)
    setSession(data.session)
  }

  const logout = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setSession(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

### 4. Make API Requests with Auth Token

Create `/frontend/src/lib/api.ts`:

```typescript
import { supabase } from "./supabase";

const API_BASE_URL = "http://localhost:8000/api";

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  // Get session token
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new Error("Not authenticated");
  }

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${session.access_token}`, // ✅ JWT token!
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

export const api = {
  generateDemo: (count: number) =>
    apiRequest(`/transactions/generate-demo?count=${count}`, {
      method: "POST",
    }),

  getTransactions: () => apiRequest("/transactions"),
};
```

### 5. Update Login/Register Pages

Use **email** instead of username:

```tsx
// Login.tsx
<Input
  type="email"
  placeholder="your@email.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

---

## 🎯 Benefits of This Approach

✅ **Email-based auth** - Industry standard  
✅ **JWT tokens** - Secure, auto-expiring  
✅ **Row Level Security** - Database enforces user isolation  
✅ **No manual user_id headers** - Extracted from token  
✅ **Production-ready** - Built on Supabase infrastructure  
✅ **Session management** - Auto-refresh tokens

---

## 📝 Summary

**What Changed:**

- ❌ Custom `users` table → ✅ Supabase `auth.users`
- ❌ Manual password hashing → ✅ Supabase Auth API
- ❌ Custom `X-User-Id` header → ✅ JWT `Authorization: Bearer <token>`
- ❌ Frontend manages user ID → ✅ Backend extracts from token

**Flow:**

1. User registers/logs in → Supabase returns JWT token
2. Frontend stores token (Supabase handles this)
3. API requests include `Authorization: Bearer <token>`
4. Backend validates token → extracts user_id
5. Database RLS ensures user only sees their data

Ready to implement?
