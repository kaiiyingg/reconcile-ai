"""
Reports Service Layer
Generate CSV and PDF reports for transactions, predictions, and anomalies
"""
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import io
from psycopg2.extras import RealDictCursor
from app.db.connection import get_db_connection


def generate_transaction_csv(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
) -> bytes:
    """
    Generate CSV export of transactions.
    
    Args:
        user_id: UUID of the user
        start_date: Filter transactions after this date (optional)
        end_date: Filter transactions before this date (optional)
        category: Filter by category (optional)
        status: Filter by status (optional)
        
    Returns:
        bytes: CSV file content
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT 
                id,
                transaction_date,
                amount,
                category,
                description,
                source,
                status,
                created_at
            FROM transactions
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY transaction_date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(t) for t in transactions])
        
        if df.empty:
            df = pd.DataFrame(columns=[
                'id', 'transaction_date', 'amount', 'category', 
                'description', 'source', 'status', 'created_at'
            ])
        
        # Generate CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue().encode('utf-8')
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to generate CSV: {str(e)}")


def generate_summary_report(user_id: str) -> Dict[str, Any]:
    """
    Generate a summary report with key metrics.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        dict: Summary statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Transaction summary
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_revenue,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses,
                SUM(amount) as net_amount,
                AVG(amount) as avg_amount,
                MIN(transaction_date) as earliest_transaction,
                MAX(transaction_date) as latest_transaction
            FROM transactions
            WHERE user_id = %s
            """,
            (user_id,)
        )
        tx_summary = cursor.fetchone()
        
        # Category breakdown
        cursor.execute(
            """
            SELECT 
                category,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM transactions
            WHERE user_id = %s
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (user_id,)
        )
        categories = cursor.fetchall()
        
        # Status breakdown
        cursor.execute(
            """
            SELECT 
                status,
                COUNT(*) as count
            FROM transactions
            WHERE user_id = %s
            GROUP BY status
            """,
            (user_id,)
        )
        statuses = cursor.fetchall()
        
        # Source breakdown
        cursor.execute(
            """
            SELECT 
                source,
                COUNT(*) as count
            FROM transactions
            WHERE user_id = %s
            GROUP BY source
            """,
            (user_id,)
        )
        sources = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "summary": dict(tx_summary),
            "by_category": [dict(c) for c in categories],
            "by_status": [dict(s) for s in statuses],
            "by_source": [dict(s) for s in sources],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to generate summary: {str(e)}")


def generate_predictions_csv(user_id: str, model_type: Optional[str] = None) -> bytes:
    """
    Generate CSV export of predictions.
    
    Args:
        user_id: UUID of the user
        model_type: Filter by model type (optional)
        
    Returns:
        bytes: CSV file content
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT 
                id,
                model_type,
                forecast_date,
                predicted_value,
                actual_value,
                confidence_score,
                model_version,
                created_at
            FROM predictions
            WHERE user_id = %s
        """
        params = [user_id]
        
        if model_type:
            query += " AND model_type = %s"
            params.append(model_type)
        
        query += " ORDER BY forecast_date DESC"
        
        cursor.execute(query, params)
        predictions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(p) for p in predictions])
        
        if df.empty:
            df = pd.DataFrame(columns=[
                'id', 'model_type', 'forecast_date', 'predicted_value',
                'actual_value', 'confidence_score', 'model_version', 'created_at'
            ])
        
        # Generate CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue().encode('utf-8')
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to generate predictions CSV: {str(e)}")
