# backend/app/models/lease.py
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Lease(BaseModel):
    __tablename__ = 'leases'
    
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float)
    status = Column(String(50), default='active')  # active, expired, terminated
    terms = Column(Text)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="leases")
    unit = relationship("Unit", back_populates="leases")
    payments = relationship("Payment", back_populates="lease")
