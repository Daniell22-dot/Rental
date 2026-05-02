from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.interaction import Feedback, Review
from app.api.endpoints.auth import get_current_user
from app.models.users import User
from pydantic import BaseModel

router = APIRouter()

class FeedbackCreate(BaseModel):
    subject: str
    message: str

class ReviewCreate(BaseModel):
    property_id: int
    rating: float
    comment: str

@router.post("/feedback")
async def submit_feedback(
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Assuming user has a related tenant object
    tenant = current_user.tenants[0] if current_user.tenants else None
    if not tenant:
        raise HTTPException(status_code=400, detail="Only tenants can submit feedback")
        
    feedback = Feedback(
        tenant_id=tenant.id,
        subject=feedback_in.subject,
        message=feedback_in.message
    )
    db.add(feedback)
    await db.commit()
    return {"message": "Feedback submitted successfully"}

@router.post("/review")
async def submit_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tenant = current_user.tenants[0] if current_user.tenants else None
    if not tenant:
        raise HTTPException(status_code=400, detail="Only tenants can submit reviews")
        
    review = Review(
        tenant_id=tenant.id,
        property_id=review_in.property_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(review)
    await db.commit()
    return {"message": "Review submitted successfully"}

@router.get("/feedback")
async def get_all_feedback(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import desc
    from app.models.tenant import Tenant
    
    # Check if user is admin/owner
    if current_user.role not in ['admin', 'landlord', 'property_manager']:
        raise HTTPException(status_code=403, detail="Not authorized to view feedback")
        
    result = await db.execute(
        select(Feedback, Tenant, User)
        .join(Tenant, Feedback.tenant_id == Tenant.id)
        .join(User, Tenant.user_id == User.id)
        .order_by(desc(Feedback.created_at))
    )
    
    feedbacks = result.all()
    
    return [{
        "id": f.id,
        "subject": f.subject,
        "message": f.message,
        "status": f.status,
        "created_at": f.created_at,
        "tenant_name": f"{u.first_name} {u.last_name}" if u else "Unknown",
        "tenant_id": t.id
    } for f, t, u in feedbacks]
