# backend/app/api/endpoints/admin.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.config import settings
from app.core.database import get_db
from app.models.users import User
from app.models.payment import Payment
from app.models.tenant import Tenant
from app.api.endpoints.auth import get_current_user
from app.api.endpoints.dependencies import get_current_admin, get_current_owner
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SystemStatsResponse(BaseModel):
    total_revenue: str
    total_tax: str
    net_profit: str
    kra_details: str
    currency: str = "KES"
    timestamp: datetime = None

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_tenants: int
    total_properties: int
    total_revenue: float
    overdue_amount: float
    active_leases: int
    maintenance_requests: int
    currency: str = "KES"

@router.get("/", status_code=status.HTTP_200_OK)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard overview"""
    return {
        "message": "Admin Dashboard API",
        "status": "active",
        "user_role": current_user.role,
        "user_email": current_user.email
    }

@router.get("/stats", response_model=SystemStatsResponse, status_code=status.HTTP_200_OK)
async def get_system_stats(
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get system financial statistics (Kenya/KRA specific)"""
    
    # Calculate total revenue from payments
    result = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        )
    )
    total_revenue = result.scalar() or 0.0
    
    # Kenya corporate tax rate: 30% (subject to change)
    kra_tax_rate = 0.30
    
    # Baringo County land rates (annual estimate)
    land_rates = 50000  # KES
    
    tax_due = (total_revenue * kra_tax_rate) + land_rates
    net_profit = total_revenue - tax_due
    
    return SystemStatsResponse(
        total_revenue=f"Ksh {total_revenue:,.0f}",
        total_tax=f"Ksh {tax_due:,.0f}",
        net_profit=f"Ksh {net_profit:,.0f}",
        kra_details="30% Income Tax + Baringo County Land Rates",
        timestamp=datetime.utcnow()
    )

@router.get("/metrics", response_model=DashboardMetrics, status_code=status.HTTP_200_OK)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get key dashboard metrics"""
    
    # Count total tenants
    result_tenants = await db.execute(select(func.count(Tenant.id)))
    total_tenants = result_tenants.scalar() or 0
    
    # Calculate total revenue
    result_revenue = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        )
    )
    total_revenue = result_revenue.scalar() or 0.0
    
    # Calculate overdue amount
    result_overdue = await db.execute(
        select(func.sum(Payment.amount)).filter(
            Payment.status == 'overdue'
        )
    )
    overdue_amount = result_overdue.scalar() or 0.0
    
    # TODO: Add properties, leases, maintenance when models are complete
    
    return DashboardMetrics(
        total_tenants=total_tenants,
        total_properties=0,  # Placeholder
        total_revenue=total_revenue,
        overdue_amount=overdue_amount,
        active_leases=0,  # Placeholder
        maintenance_requests=0  # Placeholder
    )

@router.post("/shutdown", status_code=status.HTTP_200_OK)
async def shutdown_system(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only: Request system shutdown (requires additional confirmation)"""
    return {
        "message": "Shutdown request received - requires confirmation",
        "requires_confirmation": True
    }
