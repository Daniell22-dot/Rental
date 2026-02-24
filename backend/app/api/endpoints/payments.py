# backend/app/api/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()

@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Process a new payment"""
    payment_service = PaymentService(db)
    result = await payment_service.process_payment(payment)
    
    # Send receipt in background
    background_tasks.add_task(
        payment_service.send_payment_receipt,
        result.id
    )
    
    return result

@router.get("/tenant/{tenant_id}")
async def get_tenant_payments(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all payments for a specific tenant"""
    payment_service = PaymentService(db)
    return await payment_service.get_tenant_payment_history(tenant_id)

@router.get("/overdue")
async def get_overdue_payments(
    db: AsyncSession = Depends(get_db)
):
    """Get all overdue payments"""
    payment_service = PaymentService(db)
    return await payment_service.get_overdue_payments()