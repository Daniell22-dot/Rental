# backend/app/api/endpoints/utilities.py
# API endpoints for water and wifi utility charge management.
# The landlord/admin enters charges manually: water has units + amount, wifi has amount only.
# Also provides invoice/statement generation for tenants.
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, desc, and_, case
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.users import User
from app.models.utility import UtilityCharge
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.property import Property
from app.api.endpoints.auth import get_current_user
from app.api.endpoints.dependencies import get_current_owner

router = APIRouter()

# ── Pydantic Schemas ─────────────────────────────────────────

class UtilityChargeCreate(BaseModel):
    unit_id: int
    tenant_id: Optional[int] = None
    utility_type: str  # 'water' or 'wifi'
    units_consumed: Optional[float] = None  # Only for water
    amount: float = Field(gt=0)
    billing_month: str  # e.g. '2026-05'
    notes: Optional[str] = None

class UtilityChargeUpdate(BaseModel):
    units_consumed: Optional[float] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class UtilityChargeResponse(BaseModel):
    id: int
    unit_id: int
    tenant_id: Optional[int] = None
    utility_type: str
    units_consumed: Optional[float] = None
    amount: float
    billing_month: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    # Joined fields
    unit_number: Optional[str] = None
    tenant_name: Optional[str] = None
    property_name: Optional[str] = None

    class Config:
        from_attributes = True

class UtilityStatementResponse(BaseModel):
    tenant_name: str
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    property_name: str
    unit_number: str
    billing_month: str
    charges: List[dict]
    total_amount: float
    generated_at: datetime

class UtilityProfitSummary(BaseModel):
    total_water_income: float
    total_wifi_income: float
    total_utility_income: float
    total_water_units: float
    charge_count: int
    paid_count: int
    pending_count: int
    billing_month: Optional[str] = None
    currency: str = "KES"

# ── CRUD Endpoints ───────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_utility_charge(
    charge_in: UtilityChargeCreate,
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Create a new utility charge (water or wifi) for a unit."""
    if charge_in.utility_type not in ('water', 'wifi'):
        raise HTTPException(status_code=400, detail="utility_type must be 'water' or 'wifi'")
    
    if charge_in.utility_type == 'water' and charge_in.units_consumed is None:
        raise HTTPException(status_code=400, detail="Water charges require units_consumed")
    
    # Verify unit exists
    result = await db.execute(select(Unit).where(Unit.id == charge_in.unit_id))
    unit = result.scalars().first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Auto-assign tenant if not provided — pick the active tenant on this unit
    tenant_id = charge_in.tenant_id
    if not tenant_id:
        result = await db.execute(
            select(Tenant.id).where(
                and_(Tenant.unit_id == charge_in.unit_id, Tenant.status == 'active')
            )
        )
        tenant_row = result.scalars().first()
        if tenant_row:
            tenant_id = tenant_row
    
    new_charge = UtilityCharge(
        unit_id=charge_in.unit_id,
        tenant_id=tenant_id,
        utility_type=charge_in.utility_type,
        units_consumed=charge_in.units_consumed if charge_in.utility_type == 'water' else None,
        amount=charge_in.amount,
        billing_month=charge_in.billing_month,
        notes=charge_in.notes,
        created_by_user_id=current_user.id,
        status='pending'
    )
    db.add(new_charge)
    await db.commit()
    await db.refresh(new_charge)
    
    return {
        "success": True,
        "message": f"{charge_in.utility_type.capitalize()} charge of Ksh {charge_in.amount:,.2f} added successfully",
        "charge_id": new_charge.id
    }


@router.get("/", response_model=List[UtilityChargeResponse])
async def list_utility_charges(
    utility_type: Optional[str] = Query(None, description="Filter by 'water' or 'wifi'"),
    billing_month: Optional[str] = Query(None, description="Filter by billing month e.g. '2026-05'"),
    unit_id: Optional[int] = Query(None, description="Filter by unit ID"),
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """List all utility charges with optional filters."""
    query = (
        select(
            UtilityCharge,
            Unit.unit_number,
            Property.name.label("property_name"),
            func.concat(Tenant.first_name, ' ', Tenant.last_name).label("tenant_name")
        )
        .outerjoin(Unit, UtilityCharge.unit_id == Unit.id)
        .outerjoin(Property, Unit.property_id == Property.id)
        .outerjoin(Tenant, UtilityCharge.tenant_id == Tenant.id)
        .order_by(desc(UtilityCharge.created_at))
    )
    
    if utility_type:
        query = query.where(UtilityCharge.utility_type == utility_type)
    if billing_month:
        query = query.where(UtilityCharge.billing_month == billing_month)
    if unit_id:
        query = query.where(UtilityCharge.unit_id == unit_id)
    
    result = await db.execute(query)
    rows = result.all()
    
    charges = []
    for row in rows:
        charge = row[0]
        charges.append(UtilityChargeResponse(
            id=charge.id,
            unit_id=charge.unit_id,
            tenant_id=charge.tenant_id,
            utility_type=charge.utility_type,
            units_consumed=charge.units_consumed,
            amount=charge.amount,
            billing_month=charge.billing_month,
            status=charge.status,
            notes=charge.notes,
            created_at=charge.created_at,
            unit_number=row[1],
            property_name=row[2],
            tenant_name=row[3]
        ))
    
    return charges


@router.put("/{charge_id}")
async def update_utility_charge(
    charge_id: int,
    update_in: UtilityChargeUpdate,
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Update a utility charge (amount, status, notes)."""
    result = await db.execute(select(UtilityCharge).where(UtilityCharge.id == charge_id))
    charge = result.scalars().first()
    if not charge:
        raise HTTPException(status_code=404, detail="Utility charge not found")
    
    if update_in.amount is not None:
        charge.amount = update_in.amount
    if update_in.units_consumed is not None:
        charge.units_consumed = update_in.units_consumed
    if update_in.status is not None:
        charge.status = update_in.status
    if update_in.notes is not None:
        charge.notes = update_in.notes
    
    await db.commit()
    return {"success": True, "message": "Utility charge updated"}


@router.delete("/{charge_id}")
async def delete_utility_charge(
    charge_id: int,
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """Delete a utility charge."""
    result = await db.execute(select(UtilityCharge).where(UtilityCharge.id == charge_id))
    charge = result.scalars().first()
    if not charge:
        raise HTTPException(status_code=404, detail="Utility charge not found")
    
    await db.delete(charge)
    await db.commit()
    return {"success": True, "message": "Utility charge deleted"}


# ── Statement / Invoice ─────────────────────────────────────

@router.get("/statement/{unit_id}")
async def get_utility_statement(
    unit_id: int,
    billing_month: str = Query(..., description="Billing month e.g. '2026-05'"),
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a utility statement/invoice for a specific unit and billing month.
    Shows all water and wifi charges, totals, and tenant info.
    """
    # Get unit info
    result = await db.execute(
        select(Unit, Property.name.label("property_name"))
        .outerjoin(Property, Unit.property_id == Property.id)
        .where(Unit.id == unit_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    unit = row[0]
    property_name = row[1] or "N/A"
    
    # Get active tenant for this unit
    result = await db.execute(
        select(Tenant).where(
            and_(Tenant.unit_id == unit_id, Tenant.status == 'active')
        )
    )
    tenant = result.scalars().first()
    tenant_name = f"{tenant.first_name} {tenant.last_name}" if tenant else "No tenant assigned"
    tenant_email = tenant.email if tenant else None
    tenant_phone = tenant.phone if tenant else None
    
    # Get all charges for this unit and billing month
    result = await db.execute(
        select(UtilityCharge).where(
            and_(
                UtilityCharge.unit_id == unit_id,
                UtilityCharge.billing_month == billing_month
            )
        ).order_by(UtilityCharge.utility_type)
    )
    charges = result.scalars().all()
    
    charge_list = []
    total = 0.0
    for c in charges:
        item = {
            "id": c.id,
            "type": c.utility_type,
            "units_consumed": c.units_consumed,
            "amount": c.amount,
            "status": c.status,
            "notes": c.notes
        }
        charge_list.append(item)
        total += c.amount
    
    return UtilityStatementResponse(
        tenant_name=tenant_name,
        tenant_email=tenant_email,
        tenant_phone=tenant_phone,
        property_name=property_name,
        unit_number=unit.unit_number,
        billing_month=billing_month,
        charges=charge_list,
        total_amount=total,
        generated_at=datetime.utcnow()
    )


# ── Profit Summary ──────────────────────────────────────────

@router.get("/profit-summary", response_model=UtilityProfitSummary)
async def get_utility_profit_summary(
    billing_month: Optional[str] = Query(None, description="Filter by billing month"),
    current_user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a profit/income summary for utility charges.
    Shows total water income, wifi income, and overall totals.
    """
    water_filter = [UtilityCharge.utility_type == 'water']
    wifi_filter = [UtilityCharge.utility_type == 'wifi']
    all_filter = []
    
    if billing_month:
        water_filter.append(UtilityCharge.billing_month == billing_month)
        wifi_filter.append(UtilityCharge.billing_month == billing_month)
        all_filter.append(UtilityCharge.billing_month == billing_month)
    
    # Total water income
    result = await db.execute(
        select(func.coalesce(func.sum(UtilityCharge.amount), 0)).where(and_(*water_filter))
    )
    total_water = result.scalar()
    
    # Total water units
    result = await db.execute(
        select(func.coalesce(func.sum(UtilityCharge.units_consumed), 0)).where(and_(*water_filter))
    )
    total_water_units = result.scalar()
    
    # Total wifi income
    result = await db.execute(
        select(func.coalesce(func.sum(UtilityCharge.amount), 0)).where(and_(*wifi_filter))
    )
    total_wifi = result.scalar()
    
    # Counts
    count_query = select(func.count(UtilityCharge.id))
    if all_filter:
        count_query = count_query.where(and_(*all_filter))
    result = await db.execute(count_query)
    charge_count = result.scalar()
    
    # Paid count
    paid_filter = [UtilityCharge.status == 'paid']
    if all_filter:
        paid_filter.extend(all_filter)
    result = await db.execute(
        select(func.count(UtilityCharge.id)).where(and_(*paid_filter))
    )
    paid_count = result.scalar()
    
    # Pending count
    pending_filter = [UtilityCharge.status == 'pending']
    if all_filter:
        pending_filter.extend(all_filter)
    result = await db.execute(
        select(func.count(UtilityCharge.id)).where(and_(*pending_filter))
    )
    pending_count = result.scalar()
    
    return UtilityProfitSummary(
        total_water_income=total_water,
        total_wifi_income=total_wifi,
        total_utility_income=total_water + total_wifi,
        total_water_units=total_water_units,
        charge_count=charge_count,
        paid_count=paid_count,
        pending_count=pending_count,
        billing_month=billing_month
    )
