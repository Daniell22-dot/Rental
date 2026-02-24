# backend/app/api/endpoints/arrears.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.payment import Payment
from app.models.lease import Lease
from app.models.users import User
from app.api.endpoints.auth import get_current_user
from app.core.exceptions import NotFoundException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ArrearsResponse(BaseModel):
    arrears: float
    monthly_rent: Optional[float] = None
    currency: str = "KES"
    status: str  # "clear", "overdue"
    months_overdue: int = 0
    payment_history_count: int = 0

@router.get("/my", response_model=ArrearsResponse, status_code=status.HTTP_200_OK)
async def get_my_arrears(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's rent arrears"""
    # Find tenant record for current user
    result = await db.execute(
        select(Tenant).filter(Tenant.user_id == current_user.id)
    )
    tenant = result.scalars().first()
    
    if not tenant:
        raise NotFoundException(detail="No tenant record found for this user")

    # Find active lease
    result = await db.execute(
        select(Lease).filter(
            Lease.tenant_id == tenant.id,
            Lease.status == 'active'
        )
    )
    active_lease = result.scalars().first()
    
    if not active_lease:
        return ArrearsResponse(
            arrears=0,
            monthly_rent=None,
            status="clear",
            currency="KES"
        )

    # Calculate overdue amount
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.tenant_id == tenant.id,
            Payment.status.in_(['overdue', 'failed'])
        )
    )
    overdue_amount = result.scalar() or 0.0
    
    # Count total payments
    result = await db.execute(
        select(func.count(Payment.id)).filter(
            Payment.tenant_id == tenant.id
        )
    )
    payment_count = result.scalar() or 0

    # Estimate months overdue (rough calculation)
    months_overdue = int(overdue_amount / active_lease.monthly_rent) if active_lease.monthly_rent > 0 else 0

    return ArrearsResponse(
        arrears=overdue_amount,
        monthly_rent=active_lease.monthly_rent,
        status="overdue" if overdue_amount > 0 else "clear",
        currency="KES",
        months_overdue=months_overdue,
        payment_history_count=payment_count
    )

@router.get("/summary", response_model=dict)
async def get_arrears_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary of total system arrears (admin only)"""
    # Calculate total overdue across all tenants
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'overdue'
        )
    )
    total_arrears = result.scalar() or 0.0
    
    # Count tenants with arrears
    result = await db.execute(
        select(func.count(Tenant.id))
    )
    total_tenants = result.scalar() or 0
    
    return {
        "total_system_arrears": total_arrears,
        "total_tenants": total_tenants,
        "currency": "KES"
    }
