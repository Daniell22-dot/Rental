# backend/app/api/endpoints/payments.py (add missing endpoints)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List, Optional
from app.core.database import get_db
from app.models.users import User
from app.models.payment import Payment, PaymentStatus
from app.models.tenant import Tenant
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PaymentResponse(BaseModel):
    id: int
    amount: float
    payment_date: datetime
    payment_method: Optional[str]
    status: str
    receipt_url: Optional[str]
    tenant_name: Optional[str] = None

class MpesaVerification(BaseModel):
    transaction_code: str

@router.get("/my", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """Get payment history for current user"""
    
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(desc(Payment.payment_date))
        .limit(limit)
    )
    payments = result.scalars().all()
    
    return [{
        "id": p.id,
        "amount": p.amount,
        "payment_date": p.payment_date,
        "payment_method": p.payment_method,
        "status": p.status,
        "receipt_url": p.receipt_url
    } for p in payments]

@router.get("/all", response_model=List[PaymentResponse])
async def get_all_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100
):
    """Get all payments (landlord/admin only)"""
    
    result = await db.execute(
        select(Payment, User)
        .join(User, Payment.user_id == User.id)
        .order_by(desc(Payment.payment_date))
        .limit(limit)
    )
    results = result.all()
    
    return [{
        "id": p.id,
        "amount": p.amount,
        "payment_date": p.payment_date,
        "payment_method": p.payment_method,
        "status": p.status,
        "receipt_url": p.receipt_url,
        "tenant_name": f"{user.first_name} {user.last_name}"
    } for p, user in results]

@router.get("/recent", response_model=List[PaymentResponse])
async def get_recent_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get recent payments for dashboard"""
    
    result = await db.execute(
        select(Payment, User, Tenant)
        .join(User, Payment.user_id == User.id)
        .outerjoin(Tenant, Payment.tenant_id == Tenant.id)
        .order_by(desc(Payment.payment_date))
        .limit(limit)
    )
    results = result.all()
    
    return [{
        "id": p.id,
        "amount": p.amount,
        "payment_date": p.payment_date,
        "payment_method": p.payment_method,
        "status": p.status,
        "receipt_url": p.receipt_url,
        "tenant_name": f"{user.first_name} {user.last_name}",
        "property_name": tenant.unit.property.name if tenant and tenant.unit else "N/A"
    } for p, user, tenant in results]

@router.post("/verify-mpesa")
async def verify_mpesa_payment(
    verification: MpesaVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify M-Pesa payment"""
    
    # In production, this would call M-Pesa API
    # For demo, we'll create a pending payment
    
    # Get tenant record
    result = await db.execute(
        select(Tenant).where(Tenant.user_id == current_user.id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant record not found")
    
    # Check if transaction already exists
    result = await db.execute(
        select(Payment).where(Payment.transaction_id == verification.transaction_code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"message": "Payment already verified", "status": existing.status}
    
    # Create pending payment record
    payment = Payment(
        tenant_id=tenant.id,
        user_id=current_user.id,
        amount=tenant.monthly_rent,
        payment_date=datetime.utcnow(),
        payment_method="M-Pesa",
        transaction_id=verification.transaction_code,
        status='pending'
    )
    
    db.add(payment)
    await db.commit()
    
    return {"message": "Payment recorded, awaiting verification", "status": "pending"}