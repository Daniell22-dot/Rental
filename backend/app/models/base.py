# backend/app/models/base.py
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class BaseModel(Base):
    """
    Base model with common attributes
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """
        Convert model to dictionary
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }