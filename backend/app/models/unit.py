from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean # This file defines the Unit model for the Rental Management System. It includes fields for unit information, relationships to other models, and is used to store and manage unit data in the database.
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Unit(BaseModel):
    __tablename__ = 'units'
    
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    unit_number = Column(String(50), nullable=False)
    floor = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    monthly_rent = Column(Float, nullable=False)
    is_occupied = Column(Boolean, default=False)
    
    # Relationships
    property = relationship("Property", back_populates="units")
    tenants = relationship("Tenant", back_populates="unit")
    leases = relationship("Lease", back_populates="unit")
    utility_charges = relationship("UtilityCharge", back_populates="unit", cascade="all, delete-orphan")