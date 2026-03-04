"""
Transaction Service Layer
Handles all business logic for transaction operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import uuid
from decimal import Decimal

from psycopg2.extras import RealDictCursor, execute_values
from app.db.connection import get_db_connection
from app.domain.transaction import TransactionResponse


def upload_transactions(df: pd.DataFrame, user_id: str) -> Dict[str, Any]:
    """
    Validates and inserts CSV/uploaded data into database.
    
    Args:
        df: Pandas DataFrame with transaction data (columns: transaction_date, amount, category, description, source, status)
        user_id: UUID of the user uploading transactions
        
    Returns:
        dict: {"uploaded_count": int, "failed_count": int, "errors": List[str]}
    """
    
    # Validate required columns
    required_columns = ["transaction_date", "amount", "category"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return {
            "uploaded_count": 0,
            "failed_count": len(df),
            "errors": [f"Missing required columns: {', '.join(missing_columns)}"]
        }
    
    # Normalize data
    df["category"] = df["category"].astype(str).str.strip().str.lower()
    
    # Prepare records for insertion
    records = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Validate amount is not zero
            amount = float(row["amount"])
            if amount == 0:
                errors.append(f"Row {idx + 1}: Amount cannot be zero")
                continue
            
            # Parse transaction date
            transaction_date = pd.to_datetime(row["transaction_date"])
            
            # Prepare record tuple
            records.append((
                str(uuid.uuid4()),                          # id
                user_id,                                    # user_id
                transaction_date,                           # transaction_date
                amount,                                     # amount
                row["category"],                            # category
                str(row.get("description", "")),            # description
                "uploaded",                                 # source
                row.get("status", "completed")              # status
            ))
            
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")
    
    # Insert valid records into database
    if records:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            execute_values(
                cursor,
                """
                INSERT INTO transactions
                (id, user_id, transaction_date, amount, category, description, source, status)
                VALUES %s
                """,
                records
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise Exception(f"Database error: {str(e)}")
    
    return {
        "uploaded_count": len(records),
        "failed_count": len(df) - len(records),
        "errors": errors if errors else None
    }


def generate_demo_transactions(count: int, user_id: str, save_to_db: bool = True, clear_existing: bool = True) -> Dict[str, Any]:
    """
    Generates mock/demo transaction data.
    
    Args:
        count: Number of demo transactions to generate
        user_id: UUID of the user
        save_to_db: If True, saves to database. If False, returns data only.
        clear_existing: If True, deletes old demo data before inserting new (default: True)
        
    Returns:
        dict: {"uploaded_count": int, "message": str, "cleared_count": int (optional), "data": List[Dict] (optional)}
    """
    import random
    
    # Demo categories and their typical amount ranges
    categories_config = {
        "revenue": (1000, 15000),
        "expense": (-5000, -100),
        "marketing": (-2000, -500),
        "operations": (-3000, -200),
        "sales": (500, 8000),
        "payroll": (-10000, -2000)
    }
    
    statuses = ["completed", "completed", "completed", "reconciled"]
    
    # Generate transactions over the past 90 days
    start_date = datetime.now() - timedelta(days=90)
    
    records = []
    for i in range(count):
        # Random date within the last 90 days
        transaction_date = start_date + timedelta(days=random.randint(0, 90))
        
        # Random category and appropriate amount
        category = random.choice(list(categories_config.keys()))
        min_amount, max_amount = categories_config[category]
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        records.append((
            str(uuid.uuid4()),
            user_id,
            transaction_date,
            amount,
            category,
            f"Demo {category} transaction {i + 1}",
            "generated",  
            random.choice(statuses)
        ))
    
    # If not saving to DB, return data for CSV download
    if not save_to_db:
        data = [
            {
                "id": record[0],
                "user_id": record[1],
                "transaction_date": record[2].isoformat(),
                "amount": record[3],
                "category": record[4],
                "description": record[5],
                "source": record[6],
                "status": record[7]
            }
            for record in records
        ]
        
        return {
            "uploaded_count": 0,
            "message": f"Generated {count} demo transactions for download",
            "data": data
        }
    
    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cleared_count = 0
        
        # Step 1: Clear existing demo transactions (if requested)
        if clear_existing:
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE user_id = %s AND source = 'generated'
                """,
                (user_id,)
            )
            cleared_count = cursor.rowcount
        
        # Step 2: Insert new demo transactions (batch insert for speed)
        execute_values(
            cursor,
            """
            INSERT INTO transactions
            (id, user_id, transaction_date, amount, category, description, source, status)
            VALUES %s
            """,
            records,
            page_size=100  # Batch in chunks of 100 (optimal for performance)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        message = f"Successfully generated {count} demo transactions"
        if cleared_count > 0:
            message += f" (cleared {cleared_count} old demo transactions)"
        
        return {
            "uploaded_count": count,
            "cleared_count": cleared_count,
            "message": message
        }
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise Exception(f"Failed to generate demo data: {str(e)}")


def fetch_transactions(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query transactions with filters.
    
    Args:
        user_id: UUID of the user
        start_date: Filter from this date onwards
        end_date: Filter up to this date
        category: Filter by category name
        status: Filter by transaction status
        limit: Maximum results to return
        offset: Results to skip (pagination)
        
    Returns:
        dict: {"total": int, "transactions": List[TransactionResponse]}
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Build dynamic query with filters
        query = "SELECT * FROM transactions WHERE user_id = %s"
        params = [user_id]
        
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        if category:
            query += " AND category = %s"
            params.append(category.lower())
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        # Get total count before pagination
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]
        
        # Add ordering and pagination
        query += " ORDER BY transaction_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # Execute main query
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "transactions": [TransactionResponse(**t) for t in transactions]
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to fetch transactions: {str(e)}")


def fetch_transaction(transaction_id: str, user_id: str) -> Optional[TransactionResponse]:
    """
    Get a single transaction by ID.
    
    Args:
        transaction_id: UUID of the transaction
        user_id: UUID of the user (for authorization)
        
    Returns:
        TransactionResponse or None if not found
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """
            SELECT * FROM transactions
            WHERE id = %s AND user_id = %s
            """,
            (transaction_id, user_id)
        )
        
        transaction = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not transaction:
            return None
        
        return TransactionResponse(**transaction)
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to fetch transaction: {str(e)}")


def calculate_summary(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Compute dashboard KPIs and summary statistics.
    
    Args:
        user_id: UUID of the user
        days: Number of days to include (default: 30)
        
    Returns:
        dict: Summary with revenue, expenses, balance, category breakdown, etc.
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get total transactions count
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM transactions
            WHERE user_id = %s AND transaction_date >= %s
            """,
            (user_id, start_date)
        )
        total_transactions = cursor.fetchone()["total"]
        
        # Calculate revenue, expenses, and net balance
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_revenue,
                COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) as total_expenses,
                COALESCE(SUM(amount), 0) as net_balance,
                COALESCE(AVG(amount), 0) as avg_amount
            FROM transactions
            WHERE user_id = %s AND transaction_date >= %s
            """,
            (user_id, start_date)
        )
        financial_summary = cursor.fetchone()
        
        # Breakdown by category
        cursor.execute(
            """
            SELECT
                category,
                COUNT(*) as count,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(AVG(amount), 0) as avg_amount
            FROM transactions
            WHERE user_id = %s AND transaction_date >= %s
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (user_id, start_date)
        )
        category_breakdown = cursor.fetchall()
        
        # Breakdown by status
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM transactions
            WHERE user_id = %s AND transaction_date >= %s
            GROUP BY status
            """,
            (user_id, start_date)
        )
        status_breakdown = cursor.fetchall()
        
        # Get recent transactions (last 10)
        cursor.execute(
            """
            SELECT * FROM transactions
            WHERE user_id = %s
            ORDER BY transaction_date DESC
            LIMIT 10
            """,
            (user_id,)
        )
        recent_transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total_transactions": total_transactions,
            "total_revenue": float(financial_summary["total_revenue"]),
            "total_expenses": float(financial_summary["total_expenses"]),
            "net_balance": float(financial_summary["net_balance"]),
            "avg_transaction_amount": float(financial_summary["avg_amount"]),
            "transactions_by_category": {
                row["category"]: {
                    "count": row["count"],
                    "total_amount": float(row["total_amount"]),
                    "avg_amount": float(row["avg_amount"])
                }
                for row in category_breakdown
            },
            "transactions_by_status": {
                row["status"]: row["count"]
                for row in status_breakdown
            },
            "recent_transactions": [TransactionResponse(**t) for t in recent_transactions],
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to calculate summary: {str(e)}")


def update_transaction_status(
    transaction_id: str,
    user_id: str,
    status: str
) -> Optional[TransactionResponse]:
    """
    Update transaction status.
    
    Args:
        transaction_id: UUID of the transaction
        user_id: UUID of the user (for authorization)
        status: New status ('pending', 'completed', 'reconciled')
        
    Returns:
        Updated TransactionResponse or None if not found
    """
    
    # Validate status
    valid_statuses = ["pending", "completed", "reconciled"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Update transaction status
        cursor.execute(
            """
            UPDATE transactions
            SET status = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING *
            """,
            (status, transaction_id, user_id)
        )
        
        updated_transaction = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        if not updated_transaction:
            return None
        
        return TransactionResponse(**updated_transaction)
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise Exception(f"Failed to update transaction status: {str(e)}")


def delete_transactions_by_source(user_id: str, source: str) -> int:
    """
    Delete all transactions from a specific source (used for demo data refresh).
    
    Args:
        user_id: UUID of the user
        source: Source filter ('demo', 'csv_upload', 'manual', 'api')
        
    Returns:
        int: Number of transactions deleted
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            DELETE FROM transactions
            WHERE user_id = %s AND source = %s
            """,
            (user_id, source)
        )
        
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise Exception(f"Failed to bulk delete transactions: {str(e)}")


def generate_demo_csv(count: int = 100) -> pd.DataFrame:
    """
    Generates demo transaction data as CSV/DataFrame for download.
    
    Args:
        count: Number of demo transactions to generate
        
    Returns:
        pd.DataFrame: DataFrame ready for CSV export
    """
    import random
    
    # Demo categories and their typical amount ranges
    categories_config = {
        "revenue": (1000, 15000),
        "expense": (-5000, -100),
        "marketing": (-2000, -500),
        "operations": (-3000, -200),
        "sales": (500, 8000),
        "payroll": (-10000, -2000)
    }
    
    statuses = ["completed", "completed", "completed", "reconciled"]
    
    # Generate transactions over the past 90 days
    start_date = datetime.now() - timedelta(days=90)
    
    data = []
    for i in range(count):
        # Random date within the last 90 days
        transaction_date = start_date + timedelta(days=random.randint(0, 90))
        
        # Random category and appropriate amount
        category = random.choice(list(categories_config.keys()))
        min_amount, max_amount = categories_config[category]
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        data.append({
            "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "category": category,
            "description": f"Demo {category} transaction {i + 1}",
            "status": random.choice(statuses)
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df
