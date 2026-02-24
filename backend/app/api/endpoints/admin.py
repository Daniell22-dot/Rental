from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.config import settings

router = APIRouter()

@router.get("/")
async def get_admin_dashboard():
    return {"message": "Admin Dashboard API", "status": "active"}

@router.get("/stats")
async def get_system_stats():
    # Baringo County / Kenya specific statistics (Placeholder data)
    total_revenue = 2500000  # KES
    kra_tax_rate = 0.30       # 30% Corporate Tax or similar
    land_rates = 50000        # Local Baringo rates
    
    tax_due = (total_revenue * kra_tax_rate) + land_rates
    net_profit = total_revenue - tax_due
    
    return {
        "total_revenue": f"Ksh {total_revenue:,.0f}",
        "total_tax": f"Ksh {tax_due:,.0f}",
        "net_profit": f"Ksh {net_profit:,.0f}",
        "kra_details": "30% Income Tax + Baringo Land Rates"
    }
