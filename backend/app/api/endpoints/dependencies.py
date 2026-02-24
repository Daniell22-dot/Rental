# backend/app/api/endpoints/dependencies.py
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.users import User, UserRole
from app.api.endpoints.auth import get_current_user
from typing import Optional

async def get_current_owner(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is an owner"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this resource"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_caretaker(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is caretaker or owner"""
    if current_user.role not in [UserRole.CARETAKER, UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Caretaker access required"
        )
    return current_user

class PaginationParams:
    """Common pagination parameters"""
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    ):
        self.skip = skip
        self.limit = limit

async def get_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginationParams:
    """Get pagination parameters from query"""
    return PaginationParams(skip=skip, limit=limit)
