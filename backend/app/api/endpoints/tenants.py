from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.tenant import Tenant
from pydantic import BaseModel

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

@router.get("/", response_model=List[TenantSchema])
async def get_tenants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant))
    return result.scalars().all()