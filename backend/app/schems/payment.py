# backend/app/schemas/payment.py
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List, Dict
from decimal import Decimal

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: str = Field(..., description="Method of payment")
    due_date: datetime
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    tenant_id: int
    lease_id: int
    payment_type: str = "rent"
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    receipt_sent: Optional[bool] = None
    notes: Optional[str] = None

class PaymentInDB(PaymentBase):
    id: int
    uuid: str
    payment_number: str
    tenant_id: int
    lease_id: int
    user_id: Optional[int]
    status: str
    payment_date: datetime
    transaction_id: Optional[str]
    late_fee_applied: bool
    late_fee_amount: float
    receipt_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PaymentResponse(PaymentInDB):
    tenant_name: Optional[str] = None
    property_name: Optional[str] = None
    unit_number: Optional[str] = None
    
    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"

class PaymentSummary(BaseModel):
    total_paid: float
    total_pending: float
    total_overdue: float
    payment_count: int
    last_payment_date: Optional[datetime]
    next_due_date: Optional[date]
    
    class Config:
        from_attributes = True

class PaymentReceipt(BaseModel):
    receipt_number: str
    payment_date: datetime
    amount: float
    tenant_name: str
    property_address: str
    payment_method: str
    transaction_id: str
    
    def generate_html(self):
        """Generate HTML receipt"""
        pass

# Tenant Schema
class TenantBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

class TenantCreate(TenantBase):
    user_id: Optional[int] = None
    unit_id: Optional[int] = None
    lease_start_date: Optional[date] = None
    lease_end_date: Optional[date] = None
    monthly_rent: Optional[float] = None

class TenantResponse(TenantBase):
    id: int
    uuid: str
    unit_id: Optional[int]
    status: str
    lease_status: str
    payment_status: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Property Schema
class PropertyBase(BaseModel):
    name: str
    address_line1: str
    city: str
    state: str
    zip_code: str
    property_type: str
    total_units: int = 1

class PropertyCreate(PropertyBase):
    owner_id: int
    description: Optional[str] = None
    amenities: Optional[List[str]] = []

class PropertyResponse(PropertyBase):
    id: int
    uuid: str
    owner_id: int
    status: str
    total_rental_income: float
    occupancy_rate: float
    created_at: datetime
    
    class Config:
        from_attributes = True