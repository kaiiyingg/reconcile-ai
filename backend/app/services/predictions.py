"""
Prediction Service Layer
Handles ML prediction logic for forecasting transaction amounts
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import numpy as np
from psycopg2.extras import RealDictCursor, execute_values
from app.db.connection import get_db_connection


def generate_predictions(user_id: str, days_ahead: int = 7, model_type: str = "simple_average") -> Dict[str, Any]:
    """
    Generate predictions for future transaction amounts.
    
    Args:
        user_id: UUID of the user
        days_ahead: Number of days to forecast (1-90)
        model_type: Type of model to use ('simple_average', 'moving_average', 'linear_trend')
        
    Returns:
        dict: {"predictions": List[Dict], "message": str, "model_type": str}
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Fetch historical transactions (last 90 days)
        cursor.execute(
            """
            SELECT transaction_date, amount, category
            FROM transactions
            WHERE user_id = %s 
              AND status = 'completed'
              AND transaction_date >= NOW() - INTERVAL '90 days'
            ORDER BY transaction_date DESC
            """,
            (user_id,)
        )
        transactions = cursor.fetchall()
        
        if len(transactions) < 5:
            cursor.close()
            conn.close()
            raise Exception("Need at least 5 transactions to generate predictions")
        
        # Simple prediction models
        predictions = []
        
        if model_type == "simple_average":
            # Calculate average amount per day
            avg_amount = sum(float(t['amount']) for t in transactions) / len(transactions)
            confidence = 0.65
            
        elif model_type == "moving_average":
            # Use last 7 days average
            recent = transactions[:min(7, len(transactions))]
            avg_amount = sum(float(t['amount']) for t in recent) / len(recent)
            confidence = 0.70
            
        elif model_type == "linear_trend":
            # Simple linear regression on amounts over time
            amounts = [float(t['amount']) for t in transactions]
            days = list(range(len(amounts)))
            
            if len(amounts) > 1:
                # Calculate slope
                mean_days = sum(days) / len(days)
                mean_amounts = sum(amounts) / len(amounts)
                
                numerator = sum((days[i] - mean_days) * (amounts[i] - mean_amounts) for i in range(len(days)))
                denominator = sum((days[i] - mean_days) ** 2 for i in range(len(days)))
                
                slope = numerator / denominator if denominator != 0 else 0
                intercept = mean_amounts - slope * mean_days
                
                avg_amount = intercept + slope * len(amounts)
                confidence = 0.75
            else:
                avg_amount = amounts[0]
                confidence = 0.60
        else:
            avg_amount = sum(float(t['amount']) for t in transactions) / len(transactions)
            confidence = 0.65
        
        # Generate predictions for next N days
        base_date = datetime.now()
        
        for day in range(1, days_ahead + 1):
            forecast_date = base_date + timedelta(days=day)
            
            # Add some variance (±15%)
            variance = avg_amount * 0.15 * (np.random.random() - 0.5) * 2
            predicted_value = round(avg_amount + variance, 2)
            
            predictions.append({
                "forecast_date": forecast_date,
                "predicted_value": predicted_value,
                "confidence_score": round(confidence - (day * 0.01), 2),  # Confidence decreases with time
                "model_type": model_type
            })
        
        # Optionally save predictions to database
        records = [
            (
                str(uuid.uuid4()),
                user_id,
                model_type,
                pred["forecast_date"],
                pred["predicted_value"],
                None,  # actual_value (will be filled later)
                pred["confidence_score"],
                "v1.0"  # model_version
            )
            for pred in predictions
        ]
        
        # Clear old predictions for this user and model
        cursor.execute(
            """
            DELETE FROM predictions
            WHERE user_id = %s AND model_type = %s AND forecast_date >= NOW()
            """,
            (user_id, model_type)
        )
        
        # Insert new predictions
        execute_values(
            cursor,
            """
            INSERT INTO predictions
            (id, user_id, model_type, forecast_date, predicted_value, actual_value, confidence_score, model_version)
            VALUES %s
            """,
            records
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "predictions": predictions,
            "message": f"Generated {len(predictions)} predictions using {model_type} model",
            "model_type": model_type,
            "days_ahead": days_ahead
        }
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise Exception(f"Failed to generate predictions: {str(e)}")


def fetch_predictions(
    user_id: str,
    model_type: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Fetch predictions from database.
    
    Args:
        user_id: UUID of the user
        model_type: Filter by model type (optional)
        start_date: Filter predictions after this date (optional)
        end_date: Filter predictions before this date (optional)
        limit: Maximum number of predictions to return
        
    Returns:
        dict: {"total": int, "predictions": List[Dict]}
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Build query with filters
        query = """
            SELECT id, user_id, model_type, forecast_date, predicted_value, 
                   actual_value, confidence_score, model_version, created_at
            FROM predictions
            WHERE user_id = %s
        """
        params = [user_id]
        
        if model_type:
            query += " AND model_type = %s"
            params.append(model_type)
        
        if start_date:
            query += " AND forecast_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND forecast_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY forecast_date ASC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        predictions = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM predictions WHERE user_id = %s"
        count_params = [user_id]
        
        if model_type:
            count_query += " AND model_type = %s"
            count_params.append(model_type)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "predictions": [dict(p) for p in predictions]
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to fetch predictions: {str(e)}")


def get_prediction_accuracy(user_id: str, model_type: str = None) -> Dict[str, Any]:
    """
    Calculate accuracy metrics for predictions vs actual values.
    
    Args:
        user_id: UUID of the user
        model_type: Filter by model type (optional)
        
    Returns:
        dict: {"mae": float, "rmse": float, "mape": float, "count": int}
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT predicted_value, actual_value
            FROM predictions
            WHERE user_id = %s 
              AND actual_value IS NOT NULL
              AND forecast_date <= NOW()
        """
        params = [user_id]
        
        if model_type:
            query += " AND model_type = %s"
            params.append(model_type)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not results:
            return {
                "mae": 0,
                "rmse": 0,
                "mape": 0,
                "count": 0,
                "message": "No predictions with actual values found"
            }
        
        # Calculate metrics
        errors = [abs(float(r['predicted_value']) - float(r['actual_value'])) for r in results]
        squared_errors = [e ** 2 for e in errors]
        
        mae = sum(errors) / len(errors)
        rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5
        
        # MAPE (Mean Absolute Percentage Error)
        mape_values = [
            abs(float(r['predicted_value']) - float(r['actual_value'])) / abs(float(r['actual_value']))
            for r in results if float(r['actual_value']) != 0
        ]
        mape = (sum(mape_values) / len(mape_values) * 100) if mape_values else 0
        
        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "count": len(results),
            "model_type": model_type
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Failed to calculate accuracy: {str(e)}")
