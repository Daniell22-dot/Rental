# backend/app/models/tenant.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Tenant(BaseModel):
    __tablename__ = 'tenants'
    
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    employer = Column(String(200))
    annual_income = Column(Float)
    unit_id = Column(Integer, ForeignKey('units.id'))
    status = Column(String(50), default='active')
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="tenants")
    unit = relationship("Unit", back_populates="tenants")
    leases = relationship("Lease", back_populates="tenant")
    payments = relationship("Payment", back_populates="tenant")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")
    documents = relationship("Document", back_populates="tenant")