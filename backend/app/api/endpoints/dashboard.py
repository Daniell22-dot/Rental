# backend/app/api/endpoints/dashboard.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_db
from app.models.users import User
from app.models.payment import Payment
from app.models.tenant import Tenant
from app.models.lease import Lease
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class DashboardStats(BaseModel):
    total_properties: int
    total_tenants: int
    active_leases: int
    total_revenue: float
    overdue_payments: float
    pending_payments: float
    currency: str = "KES"
    last_updated: datetime

@router.get("/", response_model=DashboardStats, status_code=status.HTTP_200_OK)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for authenticated user"""
    
    # Count total tenants
    result = await db.execute(select(func.count(Tenant.id)))
    total_tenants = result.scalar() or 0
    
    # Count active leases
    result = await db.execute(
        select(func.count(Lease.id)).filter(Lease.status == 'active')
    )
    active_leases = result.scalar() or 0
    
    # Calculate total revenue
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        )
    )
    total_revenue = result.scalar() or 0.0
    
    # Calculate overdue payments
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'overdue'
        )
    )
    overdue_payments = result.scalar() or 0.0
    
    # Calculate pending payments
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'pending'
        )
    )
    pending_payments = result.scalar() or 0.0
    
    # TODO: Count total properties when Property model endpoints are complete
    total_properties = 0
    
    return DashboardStats(
        total_properties=total_properties,
        total_tenants=total_tenants,
        active_leases=active_leases,
        total_revenue=total_revenue,
        overdue_payments=overdue_payments,
        pending_payments=pending_payments,
        last_updated=datetime.utcnow()
    )

@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get quick summary for dashboard cards"""
    result = await db.execute(select(func.count(Tenant.id)))
    tenants = result.scalar() or 0
    
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        )
    )
    revenue = result.scalar() or 0.0
    
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'overdue'
        )
    )
    arrears = result.scalar() or 0.0
    
    return {
        "tenants": tenants,
        "revenue_ksh": f"{revenue:,.0f}",
        "arrears_ksh": f"{arrears:,.0f}",
        "user_role": current_user.role
    }

