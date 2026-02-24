# backend/app/models/payment.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Payment(BaseModel):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    lease_id = Column(Integer, ForeignKey('leases.id'))
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))  # bank_transfer, cash, check, card, mpesa
    status = Column(String(20), default='pending')  # pending, paid, overdue, failed
    transaction_id = Column(String(100), unique=True)
    mpesa_code = Column(String(20), unique=True, index=True)
    receipt_url = Column(String(500))
    notes = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="payments")
    lease = relationship("Lease", back_populates="payments")
    user = relationship("User", back_populates="payments")