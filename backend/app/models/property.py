# backend/app/models/property.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseModel

class Property(BaseModel):
    __tablename__ = 'properties'
    
    # Basic Information
    name = Column(String(200), nullable=False)
    property_type = Column(String(50))  # apartment, house, commercial, etc.
    description = Column(Text)
    year_built = Column(Integer)
    
    # Address
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(50), default='USA')
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Property Details
    total_units = Column(Integer, default=1)
    total_area = Column(Float)  # in sq ft
    lot_size = Column(Float)  # in sq ft
    parking_spaces = Column(Integer, default=0)
    stories = Column(Integer, default=1)
    
    # Features
    amenities = Column(JSONB, default=list)  # ['pool', 'gym', 'laundry']
    utilities_included = Column(JSONB, default=list)  # ['water', 'gas', 'electricity']
    
    # Financial
    purchase_price = Column(Float)
    current_value = Column(Float)
    annual_taxes = Column(Float)
    insurance_cost = Column(Float)
    
    # Status
    status = Column(String(50), default='available')  # available, occupied, maintenance
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="related_property", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    
    @property
    def total_rental_income(self):
        return sum(unit.monthly_rent for unit in self.units if unit.is_rented)
    
    @property
    def occupancy_rate(self):
        if not self.units:
            return 0
        rented = sum(1 for unit in self.units if unit.is_rented)
        return (rented / len(self.units)) * 100

class Unit(BaseModel):
    __tablename__ = 'units'
    
    unit_number = Column(String(50), nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id'))
    bedrooms = Column(Integer, default=1)
    bathrooms = Column(Float, default=1)
    area = Column(Float)  # sq ft
    floor = Column(Integer)
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float)
    is_rented = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    
    # Unit specific features
    amenities = Column(JSONB, default=list)
    
    # Relationships
    related_property = relationship("Property", back_populates="units")
    leases = relationship("Lease", back_populates="unit")
    tenants = relationship("Tenant", back_populates="unit")
    
    @property
    def current_tenant(self):
        active_lease = next(
            (lease for lease in self.leases if lease.status == 'active'),
            None
        )
        return active_lease.tenant if active_lease else None