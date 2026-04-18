from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.models.tenant import Tenant
from pydantic import BaseModel
from typing import List

router = APIRouter()

class TenantSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str = None
    unit_id: int = None
    status: str

    class Config:
        from_attributes = True

class RoomDetails(BaseModel):
    room_number: str
    condition: str
    notes: str = ""

@router.post("/room-details")
async def update_room_details(
    details: RoomDetails,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Tenant).where(Tenant.user_id == current_user.id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant profile not found")
    
    await db.execute(
        update(Tenant)
        .where(Tenant.user_id == current_user.id)
        .values(
            room_number=details.room_number,
            notes=f"Condition: {details.condition}\\n{details.notes}"
        )
    )
    await db.commit()
    return {"message": "Room details updated"}

@router.get("/", response_model=List[TenantSchema])
async def get_tenants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant))
    return result.scalars().all()
