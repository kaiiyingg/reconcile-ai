"""
Reports Routes
Generate and export transaction reports (CSV, PDF, summary statistics)
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import io
from app.dependencies.auth import get_current_user
from app.services import reports as reports_service

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


@router.get("/transactions/csv")
async def export_transactions_csv(
    current_user: dict = Depends(get_current_user),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    Export transactions as CSV file.
    Filters: start_date, end_date, category, status
    """
    try:
        # Parse dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        csv_content = reports_service.generate_transaction_csv(
            user_id=current_user["id"],
            start_date=start,
            end_date=end,
            category=category,
            status=status
        )
        
        filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/summary")
async def get_summary_report(
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary statistics report.
    Includes totals, averages, category breakdown, status breakdown.
    """
    try:
        summary = reports_service.generate_summary_report(
            user_id=current_user["id"]
        )
        return summary
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/predictions/csv")
async def export_predictions_csv(
    current_user: dict = Depends(get_current_user),
    model_type: Optional[str] = Query(None, description="Filter by model type")
):
    """
    Export predictions as CSV file.
    Optional filter: model_type
    """
    try:
        csv_content = reports_service.generate_predictions_csv(
            user_id=current_user["id"],
            model_type=model_type
        )
        
        filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        return {"error": str(e)}