from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.property import Property
from pydantic import BaseModel

router = APIRouter()

class PropertySchema(BaseModel):
    id: int
    name: str
    address_line1: str
    city: str
    status: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PropertySchema])
async def get_properties(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Property))
    return result.scalars().all()
