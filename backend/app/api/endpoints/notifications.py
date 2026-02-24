from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.notification import Notification
from app.api.endpoints.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationOut])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification).filter(
            Notification.id == notification_id, 
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    await db.commit()
    return {"message": "Marked as read"}
