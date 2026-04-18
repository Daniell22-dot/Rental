from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.models.tenant import Tenant
import os
import base64
from datetime import datetime
import uuid

router = APIRouter()

UPLOAD_DIR = "static/uploads/profiles"
# Only create directory if NOT on Vercel (read-only FS)
if not os.environ.get("VERCEL"):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/profile-photo")
async def upload_profile_photo(
    photo_data: str = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Decode base64 image
        if photo_data.startswith('data:image'):
            photo_data = photo_data.split(',')[1]
        img_data = base64.b64decode(photo_data)
        
        # Generate unique filename
        filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        # Update user
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(profile_picture=f"/static/uploads/profiles/{filename}")
        )
        await db.commit()
        
        return {"profile_picture": f"/static/uploads/profiles/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")
