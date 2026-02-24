# backend/app/schemas/base.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Generic, TypeVar
from enum import Enum
from datetime import datetime

T = TypeVar('T')

# Response wrappers
class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: str
    last_name: str
    terms_accepted: bool

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# User schemas
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    CARETAKER = "caretaker"
    TENANT = "tenant"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.TENANT

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

# Payment schemas
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    OVERDUE = "overdue"

class PaymentCreate(BaseModel):
    tenant_id: int
    amount: float = Field(gt=0)
    payment_method: str
    reference: Optional[str] = None

class PaymentUpdate(BaseModel):
    status: PaymentStatus
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    tenant_id: int
    amount: float
    status: PaymentStatus
    payment_method: str
    reference: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Tenant schemas
class TenantCreate(BaseModel):
    user_id: int
    phone: str
    id_number: Optional[str] = None
    occupation: Optional[str] = None

class TenantUpdate(BaseModel):
    phone: Optional[str] = None
    occupation: Optional[str] = None
    status: Optional[str] = None

class TenantResponse(BaseModel):
    id: int
    user_id: int
    phone: str
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True

# Property schemas
class PropertyCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    total_units: int = Field(gt=0)
    owner_id: int

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class PropertyResponse(BaseModel):
    id: int
    name: str
    location: str
    total_units: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Pagination
class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response"""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
