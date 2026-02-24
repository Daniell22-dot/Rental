# backend/app/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel

class Document(BaseModel):
    __tablename__ = 'documents'
    
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    property_id = Column(Integer, ForeignKey('properties.id'))
    name = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    document_type = Column(String(100))  # lease, id_copy, payment_receipt
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
    property = relationship("Property", back_populates="documents")
    uploaded_by = relationship("User", back_populates="documents")
