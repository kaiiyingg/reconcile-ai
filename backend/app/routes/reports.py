"""
Reports routes: generate CSV and PDF reports
"""
from fastapi import APIRouter, HTTPException, Header, Query, Response
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import io
from datetime import datetime


from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/csv")
async def generate_csv_report(
    report_type: str = Query(default="transactions", regex="^(transactions|predictions|anomalies|full)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: str = Header(..., alias="x-user-id")
):
    """Generate CSV report"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if report_type == "transactions" or report_type == "full":
            query = "SELECT * FROM transactions WHERE user_id = %s"
            params = [user_id]
            
            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            cursor.execute(query, params)
            transactions = cursor.fetchall()
            
            if not transactions:
                raise HTTPException(status_code=404, detail="No data found for report")
            
            df = pd.DataFrame(transactions)
            
            output = io.StringIO()
            df.to_csv(output, index=False)
            csv_content = output.getvalue()
            
            cursor.close()
            conn.close()
            
            filename = f"transactions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        
        elif report_type == "predictions":
            query = "SELECT * FROM predictions WHERE user_id = %s"
            params = [user_id]
            
            if start_date:
                query += " AND forecast_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND forecast_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY forecast_date ASC"
            cursor.execute(query, params)
            predictions = cursor.fetchall()
            
            if not predictions:
                raise HTTPException(status_code=404, detail="No predictions found")
            
            df = pd.DataFrame(predictions)
            
            output = io.StringIO()
            df.to_csv(output, index=False)
            csv_content = output.getvalue()
            
            cursor.close()
            conn.close()
            
            filename = f"predictions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        
        elif report_type == "anomalies":
            query = """
                SELECT a.*, t.timestamp, t.amount, t.category
                FROM anomalies a
                LEFT JOIN transactions t ON a.transaction_id = t.id
                WHERE a.user_id = %s
            """
            params = [user_id]
            
            if start_date:
                query += " AND a.detected_at >= %s"
                params.append(start_date)
            if end_date:
                query += " AND a.detected_at <= %s"
                params.append(end_date)
            
            query += " ORDER BY a.detected_at DESC"
            cursor.execute(query, params)
            anomalies = cursor.fetchall()
            
            if not anomalies:
                raise HTTPException(status_code=404, detail="No anomalies found")
            
            df = pd.DataFrame(anomalies)
            
            output = io.StringIO()
            df.to_csv(output, index=False)
            csv_content = output.getvalue()
            
            cursor.close()
            conn.close()
            
            filename = f"anomalies_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/summary")
async def get_report_summary(
    user_id: str = Header(..., alias="x-user-id")
):
    """Get summary statistics for reports dashboard"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT COUNT(*) as total FROM transactions WHERE user_id = %s",
            (user_id,)
        )
        total_transactions = cursor.fetchone()['total']
        
        cursor.execute(
            "SELECT COUNT(*) as total FROM predictions WHERE user_id = %s",
            (user_id,)
        )
        total_predictions = cursor.fetchone()['total']
        
        cursor.execute(
            "SELECT COUNT(*) as total FROM anomalies WHERE user_id = %s",
            (user_id,)
        )
        total_anomalies = cursor.fetchone()['total']
        
        cursor.execute(
            """
            SELECT SUM(amount) as total_amount
            FROM transactions
            WHERE user_id = %s AND status = 'completed'
            """,
            (user_id,)
        )
        total_amount = cursor.fetchone()['total_amount'] or 0
        
        cursor.close()
        conn.close()
        
        return {
            "total_transactions": total_transactions,
            "total_predictions": total_predictions,
            "total_anomalies": total_anomalies,
            "total_amount": float(total_amount),
            "report_types": ["transactions", "predictions", "anomalies", "full"]
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")
