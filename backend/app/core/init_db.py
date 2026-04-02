# backend/app/core/init_db.py
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select, text
from app.models.users import User, UserRole
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.payment import Payment
from app.core.security import get_password_hash
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def init_admin_user(conn: AsyncConnection):
    """Create default admin user if none exists"""
    try:
        result = await conn.execute(
            select(User).where(User.email == "admin@rms.com")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin_user = User(
                email="admin@rms.com",
                username="admin",
                first_name="System",
                last_name="Administrator",
                phone="+254700000000",
                hashed_password=get_password_hash("Admin123!"),
                role=UserRole.ADMIN,
                is_verified=True,
                is_superuser=True,
                created_at=datetime.utcnow()
            )
            conn.add(admin_user)
            await conn.commit()
            logger.info("Admin user created: admin@rms.com / Admin123!")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")

async def init_test_tenant(conn: AsyncConnection):
    """Create a test tenant account for testing"""
    try:
        result = await conn.execute(
            select(User).where(User.email == "tenant@rms.com")
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            tenant_user = User(
                email="tenant@rms.com",
                username="tenant",
                first_name="Test",
                last_name="Tenant",
                phone="+254712345678",
                hashed_password=get_password_hash("Tenant123!"),
                role=UserRole.TENANT,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            conn.add(tenant_user)
            await conn.commit()
            logger.info("Tenant user created: tenant@rms.com / Tenant123!")
        else:
            logger.info("Test tenant already exists")
            
        # Also create a landlord test account
        result = await conn.execute(
            select(User).where(User.email == "landlord@rms.com")
        )
        landlord = result.scalar_one_or_none()
        
        if not landlord:
            landlord_user = User(
                email="landlord@rms.com",
                username="landlord",
                first_name="Test",
                last_name="Landlord",
                phone="+254722222222",
                hashed_password=get_password_hash("Landlord123!"),
                role=UserRole.LANDLORD,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            conn.add(landlord_user)
            await conn.commit()
            logger.info("Landlord user created: landlord@rms.com / Landlord123!")
            
    except Exception as e:
        logger.error(f"Error creating test accounts: {e}")

async def create_sample_data(conn: AsyncConnection):
    """Create sample data for testing (optional)"""
    try:
        # Check if we already have properties
        result = await conn.execute(select(Property).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("Sample data already exists")
            return
        
        # Get landlord user
        result = await conn.execute(
            select(User).where(User.email == "landlord@rms.com")
        )
        landlord = result.scalar_one_or_none()
        
        if landlord:
            # Create a sample property
            property = Property(
                name="Sunset Apartments",
                address="123 Nairobi Road, Westlands, Nairobi",
                owner_id=landlord.id,
                total_units=10,
                created_at=datetime.utcnow()
            )
            conn.add(property)
            await conn.flush()
            
            # Create sample units
            for i in range(1, 4):
                unit = Unit(
                    property_id=property.id,
                    unit_number=f"{i:03d}",
                    floor=(i - 1) // 2 + 1,
                    bedrooms=2,
                    bathrooms=1.5,
                    monthly_rent=25000,
                    is_occupied=(i == 1),  # Only first unit occupied
                    created_at=datetime.utcnow()
                )
                conn.add(unit)
            
            await conn.commit()
            logger.info("Sample data created successfully")
            
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        await conn.rollback()