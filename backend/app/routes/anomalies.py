"""
Anomaly routes: run anomaly detection, fetch anomalies
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import random
import uuid

from app.domain.anomaly import (
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyUpdate,
    AnomalyStatsResponse
)
from app.db.connection import get_db_connection

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])


@router.post("/run")
async def run_anomaly_detection(
    threshold: float = Query(default=0.75, ge=0.0, le=1.0),
    user_id: str = Header(..., alias="x-user-id")
):
    """Run anomaly detection on transactions"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """
            SELECT id, timestamp, amount, category
            FROM transactions
            WHERE user_id = %s AND status = 'completed'
            ORDER BY timestamp DESC
            LIMIT 500
            """,
            (user_id,)
        )
        transactions = cursor.fetchall()
        
        if len(transactions) < 20:
            raise HTTPException(
                status_code=400,
                detail="Need at least 20 transactions for anomaly detection"
            )
        
        amounts = [float(t['amount']) for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        std_dev = (sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
        
        anomalies_created = 0
        
        for txn in transactions:
            amount = float(txn['amount'])
            deviation = abs(amount - avg_amount) / (std_dev + 1)
            
            anomaly_score = min(deviation / 3, 1.0)
            
            if anomaly_score >= threshold:
                if anomaly_score >= 0.9:
                    severity = 'critical'
                elif anomaly_score >= 0.8:
                    severity = 'high'
                elif anomaly_score >= 0.75:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                flagged = anomaly_score >= 0.85
                
                explanation = f"Transaction amount ${amount:.2f} deviates {deviation:.2f}σ from mean ${avg_amount:.2f}"
                
                cursor.execute(
                    """
                    INSERT INTO anomalies 
                    (id, user_id, transaction_id, anomaly_score, severity, flagged, explanation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (transaction_id) DO NOTHING
                    """,
                    (
                        uuid.uuid4(),
                        user_id,
                        txn['id'],
                        round(anomaly_score, 4),
                        severity,
                        flagged,
                        explanation
                    )
                )
                anomalies_created += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": f"Detected {anomalies_created} anomalies",
            "threshold": threshold,
            "transactions_analyzed": len(transactions),
            "anomalies_found": anomalies_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.get("", response_model=AnomalyListResponse)
async def get_anomalies(
    severity: Optional[str] = None,
    flagged: Optional[bool] = None,
    reviewed: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    user_id: str = Header(..., alias="x-user-id")
):
    """Fetch anomalies with optional filters"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT * FROM anomalies WHERE user_id = %s"
        params = [user_id]
        
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        
        if flagged is not None:
            query += " AND flagged = %s"
            params.append(flagged)
        
        if reviewed is not None:
            query += " AND reviewed = %s"
            params.append(reviewed)
        
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        query += " ORDER BY detected_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        anomalies = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return AnomalyListResponse(
            total=total,
            anomalies=[AnomalyResponse(**a) for a in anomalies]
        )
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {str(e)}")


@router.patch("/{anomaly_id}")
async def update_anomaly(
    anomaly_id: str,
    update_data: AnomalyUpdate,
    user_id: str = Header(..., alias="x-user-id")
):
    """Update anomaly (mark as reviewed, add notes, etc.)"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if update_data.flagged is not None:
            updates.append("flagged = %s")
            params.append(update_data.flagged)
        
        if update_data.reviewed is not None:
            updates.append("reviewed = %s")
            params.append(update_data.reviewed)
            if update_data.reviewed:
                updates.append("reviewed_by = %s")
                updates.append("reviewed_at = NOW()")
                params.append(user_id)
        
        if update_data.resolution_notes:
            updates.append("resolution_notes = %s")
            params.append(update_data.resolution_notes)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        query = f"UPDATE anomalies SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
        params.extend([anomaly_id, user_id])
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Anomaly updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.get("/stats", response_model=AnomalyStatsResponse)
async def get_anomaly_stats(
    user_id: str = Header(..., alias="x-user-id")
):
    """Get anomaly statistics for dashboard"""
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT COUNT(*) as total FROM anomalies WHERE user_id = %s",
            (user_id,)
        )
        total_anomalies = cursor.fetchone()['total']
        
        cursor.execute(
            "SELECT COUNT(*) as flagged FROM anomalies WHERE user_id = %s AND flagged = TRUE",
            (user_id,)
        )
        flagged_count = cursor.fetchone()['flagged']
        
        cursor.execute(
            "SELECT COUNT(*) as unreviewed FROM anomalies WHERE user_id = %s AND reviewed = FALSE",
            (user_id,)
        )
        unreviewed_count = cursor.fetchone()['unreviewed']
        
        cursor.execute(
            """
            SELECT severity, COUNT(*) as count
            FROM anomalies
            WHERE user_id = %s
            GROUP BY severity
            """,
            (user_id,)
        )
        severity_data = cursor.fetchall()
        severity_breakdown = {row['severity']: row['count'] for row in severity_data}
        
        cursor.execute(
            """
            SELECT * FROM anomalies
            WHERE user_id = %s
            ORDER BY detected_at DESC
            LIMIT 5
            """,
            (user_id,)
        )
        recent = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return AnomalyStatsResponse(
            total_anomalies=total_anomalies,
            flagged_count=flagged_count,
            unreviewed_count=unreviewed_count,
            severity_breakdown=severity_breakdown,
            recent_anomalies=[AnomalyResponse(**a) for a in recent]
        )
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
