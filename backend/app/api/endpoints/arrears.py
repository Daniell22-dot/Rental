# backend/app/api/endpoints/arrears.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.users import User
from app.models.payment import Payment
from app.models.tenant import Tenant
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ArrearsResponse(BaseModel):
    arrears: float
    last_payment_date: datetime = None
    currency: str = "KES"

@router.get("/my", response_model=ArrearsResponse)
async def get_my_arrears(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's arrears"""
    
    # Get tenant record for this user
    result = await db.execute(
        select(Tenant).where(Tenant.user_id == current_user.id)
    )
    tenant = result.scalars().first()
    
    if not tenant:
        return ArrearsResponse(arrears=0.0)
    
    # Calculate total paid
    result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.tenant_id == tenant.id,
            Payment.status == 'completed'
        )
    )
    total_paid = result.scalar() or 0.0
    
    # Calculate expected rent (simplified - should consider lease dates)
    expected_rent = tenant.monthly_rent * 1  # Current month
    
    arrears = max(0, expected_rent - total_paid)
    
    # Get last payment date
    result = await db.execute(
        select(Payment.payment_date).where(
            Payment.tenant_id == tenant.id,
            Payment.status == 'completed'
        ).order_by(Payment.payment_date.desc()).limit(1)
    )
    last_payment = result.scalar()
    
    return ArrearsResponse(
        arrears=arrears,
        last_payment_date=last_payment
    )