"""
Insights routes: generate actionable suggestions from predictions and anomalies
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

from app.routes.auth import get_current_user
from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("")
async def get_insights(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Generate actionable insights from predictions and anomalies"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    insights = []
    
    try:
        cursor.execute(
            """
            SELECT COUNT(*) as critical_count
            FROM anomalies
            WHERE user_id = %s AND severity = 'critical' AND reviewed = FALSE
            """,
            (current_user['id'],)
        )
        critical_anomalies = cursor.fetchone()['critical_count']
        
        if critical_anomalies > 0:
            insights.append({
                "type": "critical",
                "title": "Critical Anomalies Detected",
                "message": f"{critical_anomalies} critical anomalies require immediate review",
                "confidence": 0.95,
                "action": "Review anomalies in the Anomalies tab",
                "icon": "alert-triangle"
            })
        
        cursor.execute(
            """
            SELECT COUNT(*) as high_count
            FROM anomalies
            WHERE user_id = %s AND severity = 'high' AND reviewed = FALSE
            """,
            (current_user['id'],)
        )
        high_anomalies = cursor.fetchone()['high_count']
        
        if high_anomalies > 5:
            insights.append({
                "type": "warning",
                "title": "Multiple High-Severity Anomalies",
                "message": f"{high_anomalies} high-severity anomalies detected in recent transactions",
                "confidence": 0.88,
                "action": "Investigate unusual transaction patterns",
                "icon": "alert-circle"
            })
        
        cursor.execute(
            """
            SELECT predicted_amount, forecast_date, confidence_score
            FROM predictions
            WHERE user_id = %s AND forecast_date >= NOW()
            ORDER BY forecast_date ASC
            LIMIT 7
            """,
            (current_user['id'],)
        )
        upcoming_predictions = cursor.fetchall()
        
        if upcoming_predictions:
            avg_predicted = sum(float(p['predicted_amount']) for p in upcoming_predictions) / len(upcoming_predictions)
            
            cursor.execute(
                """
                SELECT AVG(amount) as avg_amount
                FROM transactions
                WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '30 days'
                """,
                (current_user['id'],)
            )
            current_avg = cursor.fetchone()['avg_amount']
            
            if current_avg and avg_predicted > float(current_avg) * 1.2:
                insights.append({
                    "type": "info",
                    "title": "Revenue Increase Predicted",
                    "message": f"Forecast shows 20%+ increase in transaction volume",
                    "confidence": 0.82,
                    "action": "Prepare for increased activity",
                    "icon": "trending-up"
                })
            elif current_avg and avg_predicted < float(current_avg) * 0.8:
                insights.append({
                    "type": "warning",
                    "title": "Revenue Decline Predicted",
                    "message": f"Forecast shows potential 20%+ decrease",
                    "confidence": 0.79,
                    "action": "Review business strategy",
                    "icon": "trending-down"
                })
        
        cursor.execute(
            """
            SELECT COUNT(*) as unreviewed
            FROM anomalies
            WHERE user_id = %s AND reviewed = FALSE
            """,
            (current_user['id'],)
        )
        unreviewed = cursor.fetchone()['unreviewed']
        
        if unreviewed > 20:
            insights.append({
                "type": "info",
                "title": "Pending Anomaly Reviews",
                "message": f"{unreviewed} anomalies pending review",
                "confidence": 1.0,
                "action": "Review and categorize anomalies",
                "icon": "file-text"
            })
        
        cursor.execute(
            """
            SELECT COUNT(*) as txn_count
            FROM transactions
            WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '7 days'
            """,
            (current_user['id'],)
        )
        recent_txns = cursor.fetchone()['txn_count']
        
        if recent_txns < 10:
            insights.append({
                "type": "info",
                "title": "Low Transaction Volume",
                "message": "Upload more transactions for better predictions",
                "confidence": 1.0,
                "action": "Upload CSV or generate demo data",
                "icon": "upload"
            })
        
        cursor.close()
        conn.close()
        
        return insights
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")
