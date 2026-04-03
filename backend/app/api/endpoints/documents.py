from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.core.database import get_db
from app.models.users import User
from app.models.document import Document
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class DocumentResponse(BaseModel):
    id: int
    title: str  # mapped from 'name' field
    document_type: Optional[str]
    file_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

@router.get("/my", response_model=List[DocumentResponse])
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """Get all documents uploaded by current user"""
    try:
        result = await db.execute(
            select(Document)
            .where(Document.uploaded_by_id == current_user.id)
            .order_by(desc(Document.uploaded_at))
            .limit(limit)
        )
        documents = result.scalars().all()
        
        return [{
            "id": doc.id,
            "title": doc.name,
            "document_type": doc.document_type,
            "file_url": doc.file_url,
            "uploaded_at": doc.uploaded_at
        } for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    doc_type: Optional[str] = None
):
    """List all documents (with optional filtering by type)"""
    try:
        query = select(Document).order_by(desc(Document.uploaded_at))
        
        if doc_type:
            query = query.where(Document.document_type == doc_type)
        
        query = query.limit(limit)
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return [{
            "id": doc.id,
            "title": doc.name,
            "document_type": doc.document_type,
            "file_url": doc.file_url,
            "uploaded_at": doc.uploaded_at
        } for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")
