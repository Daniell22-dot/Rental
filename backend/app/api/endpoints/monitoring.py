from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.core.database import get_db
from app.models.monitoring import SystemMetric, LogEntry
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HealthStatus(BaseModel):
    status: str
    db_connected: bool
    timestamp: datetime

@router.get("/health", response_model=HealthStatus)
async def get_health(db: AsyncSession = Depends(get_db)):
    # Try a simple query to verify DB connection
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except:
        pass
        
    return {
        "status": "online",
        "db_connected": db_ok,
        "timestamp": datetime.utcnow()
    }

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemMetric).order_by(SystemMetric.timestamp.desc()).limit(50))
    return result.scalars().all()

@router.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LogEntry).order_by(LogEntry.timestamp.desc()).limit(100))
    return result.scalars().all()
