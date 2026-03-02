"""
Transaction routes: upload CSV, generate mock data, fetch transactions
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import io
from datetime import datetime, timedelta
import random
import uuid

from app.models.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    CSVUploadResponse
)
from app.routes.auth import get_current_user
from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_transactions(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload CSV/Excel file with transactions"""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        required_columns = ['timestamp', 'amount', 'category']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        uploaded_count = 0
        failed_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO transactions (id, user_id, timestamp, amount, category, account_id, description, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid.uuid4(),
                        current_user['id'],
                        pd.to_datetime(row['timestamp']),
                        float(row['amount']),
                        str(row['category']),
                        str(row.get('account_id', '')),
                        str(row.get('description', '')),
                        'csv_upload'
                    )
                )
                uploaded_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return CSVUploadResponse(
            message=f"Upload complete: {uploaded_count} successful, {failed_count} failed",
            uploaded_count=uploaded_count,
            failed_count=failed_count,
            errors=errors[:10] if errors else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/generate-demo", response_model=CSVUploadResponse)
async def generate_demo_transactions(
    count: int = Query(default=100, ge=10, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Generate demo/mock transaction data"""
    
    categories = ['Revenue', 'Expense', 'Payroll', 'Marketing', 'Operations', 'Sales', 'Refund']
    accounts = ['ACC001', 'ACC002', 'ACC003', 'ACC004']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(count):
            transaction_date = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            category = random.choice(categories)
            amount = random.uniform(-5000, 10000) if category == 'Expense' else random.uniform(100, 15000)
            
            cursor.execute(
                """
                INSERT INTO transactions (id, user_id, timestamp, amount, category, account_id, description, source, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    uuid.uuid4(),
                    current_user['id'],
                    transaction_date,
                    round(amount, 2),
                    category,
                    random.choice(accounts),
                    f"Demo transaction {i+1}",
                    'demo',
                    random.choice(['completed', 'completed', 'completed', 'pending'])
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return CSVUploadResponse(
            message=f"Generated {count} demo transactions successfully",
            uploaded_count=count,
            failed_count=0
        )
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Demo generation failed: {str(e)}")


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Fetch all transactions with optional filters"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM transactions WHERE user_id = %s"
        params = [current_user['id']]
        
        if start_date:
            query += " AND timestamp >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= %s"
            params.append(end_date)
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return TransactionListResponse(
            total=total,
            transactions=[TransactionResponse(**t) for t in transactions]
        )
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single transaction by ID"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, current_user['id'])
        )
        transaction = cursor.fetchone()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        cursor.close()
        conn.close()
        
        return TransactionResponse(**transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
