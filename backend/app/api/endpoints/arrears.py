# backend/app/api/endpoints/arrears.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.payment import Payment
from app.models.lease import Lease
from app.models.users import User
from app.api.endpoints.auth import get_current_user # Assuming this exists or using a mock
from typing import Dict

router = APIRouter()

@router.get("/my")
async def get_my_arrears(db: AsyncSession = Depends(get_db)):
    # In a real app, we get tenant_id from the authenticated user
    # For now, let's mock it or find the first active tenant
    result = await db.execute(select(Tenant))
    tenant = result.scalars().first()
    if not tenant:
        return {"arrears": 0, "status": "no_tenant_record"}

    # Calculate Total Expected Rent from Active Leases
    result = await db.execute(select(Lease).filter(Lease.tenant_id == tenant.id, Lease.status == 'active'))
    active_lease = result.scalars().first()
    if not active_lease:
         return {"arrears": 0, "status": "no_active_lease"}

    # Simplistic calculation: (Months since start * monthly_rent) - total_paid
    # For demo, we'll just check for any 'overdue' or 'failed' payments
    result = await db.execute(select(func.sum(Payment.amount)).filter(
        Payment.tenant_id == tenant.id,
        Payment.status.in_(['overdue', 'failed'])
    ))
    overdue_amount = result.scalar() or 0.0

    return {
        "arrears": overdue_amount,
        "monthly_rent": active_lease.monthly_rent,
        "currency": "KES",
        "status": "overdue" if overdue_amount > 0 else "clear"
    }
