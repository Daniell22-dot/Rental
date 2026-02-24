from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentBase(BaseModel):
    amount: float
    tenant_id: int
    lease_id: int
    payment_date: datetime = datetime.now()
    payment_method: str
    status: str = "pending"

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int

    class Config:
        from_attributes = True
