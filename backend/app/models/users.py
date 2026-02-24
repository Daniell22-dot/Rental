# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class UserRole(str, enum.Enum):
    LANDLORD = "landlord"
    TENANT = "tenant"
    ADMIN = "admin"
    PROPERTY_MANAGER = "property_manager"

class User(BaseModel):
    __tablename__ = 'users'
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.TENANT)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    profile_picture = Column(String(500))
    
    # Preferences
    notification_email = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=False)
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    
    # Relationships
    properties = relationship("Property", back_populates="owner")
    tenants = relationship("Tenant", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    documents = relationship("Document", back_populates="uploaded_by")
    notifications = relationship("Notification", back_populates="user")