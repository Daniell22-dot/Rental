# dependencies.py should contain common dependencies used across multiple endpoints, such as authentication checks for different user roles (owner, admin, caretaker) and pagination parameters. This helps to keep the endpoint code clean and promotes reusability of common logic. By centralizing these dependencies, we can easily manage access control and pagination across the entire API without duplicating code in each endpoint file.
# For example, the get_current_owner dependency can be used in any endpoint that requires owner-level access, while the get_pagination dependency can be used in any endpoint that supports pagination. This approach enhances maintainability and consistency across the API.
# The main purpose of this file is to define reusable dependencies that can be easily imported and used in various endpoint modules, ensuring that access control and pagination logic is consistent and centralized throughout the application.
# By using FastAPI's Depends, we can easily integrate these dependencies into our endpoint functions, allowing for clean and efficient code that adheres to the DRY (Don't Repeat Yourself) principle.
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.users import User, UserRole
from app.api.endpoints.auth import get_current_user
from typing import Optional

#  checking if the current user is an owner or admin, and if not, raise a 403 Forbidden error. This ensures that only users with the appropriate roles can access certain endpoints that require owner-level permissions.
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