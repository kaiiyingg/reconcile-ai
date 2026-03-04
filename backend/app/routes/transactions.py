"""
Transaction routes
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import pandas as pd
import io

from app.domain.transaction import (
    TransactionResponse,
    TransactionListResponse,
    CSVUploadResponse
)
from app.dependencies.auth import get_current_user
from app.services import transactions as tx_service


router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.post("/upload", response_model=CSVUploadResponse)
async def upload_transactions(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "File must be CSV or Excel format")

    try:
        contents = await file.read()
        
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        result = tx_service.upload_transactions(df, user["id"])
        
        return CSVUploadResponse(
            message=result.get("message", "Upload complete"),
            uploaded_count=result["uploaded_count"],
            failed_count=result["failed_count"],
            errors=result.get("errors")
        )

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/generate-demo")
async def generate_demo(
    count: int = Query(default=100, ge=10, le=1000),
    user=Depends(get_current_user)
):
    try:
        print(f"Generating {count} demo transactions for user {user['id']}")
        result = tx_service.generate_demo_transactions(
            count=count,
            user_id=user["id"],
            save_to_db=True,
            clear_existing=True
        )
        print(f"Demo generation result: {result}")
        return result
    except Exception as e:
        print(f"Error generating demo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))


@router.get("/download-demo-csv")
async def download_demo_csv(count: int = Query(default=100, ge=10, le=1000)):
    try:
        df = tx_service.generate_demo_csv(count)
        
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        
        return StreamingResponse(
            io.BytesIO(stream.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=demo_transactions.csv"}
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    user=Depends(get_current_user)
):
    try:
        result = tx_service.fetch_transactions(
            user_id=user["id"],
            start_date=start_date,
            end_date=end_date,
            category=category,
            status=status,
            limit=limit,
            offset=offset
        )
        return TransactionListResponse(
            total=result["total"],
            transactions=result["transactions"]
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/summary")
async def get_summary(
    days: int = Query(default=30, ge=1, le=365),
    user=Depends(get_current_user)
):
    try:
        return tx_service.calculate_summary(user["id"], days)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    user=Depends(get_current_user)
):
    try:
        transaction = tx_service.fetch_transaction(transaction_id, user["id"])
        if not transaction:
            raise HTTPException(404, "Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.patch("/{transaction_id}/status")
async def update_status(
    transaction_id: str,
    status: str,
    user=Depends(get_current_user)
):
    try:
        updated = tx_service.update_transaction_status(transaction_id, user["id"], status)
        if not updated:
            raise HTTPException(404, "Transaction not found")
        return updated
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.delete("/bulk-delete")
async def bulk_delete(
    source: str,
    user=Depends(get_current_user)
):
    try:
        deleted = tx_service.delete_transactions_by_source(user["id"], source)
        return {"message": f"Deleted {deleted} transactions", "deleted_count": deleted}
    except Exception as e:
        raise HTTPException(500, str(e))