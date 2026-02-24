# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.api.endpoints import (
    auth, tenants, properties, payments, 
    maintenance, dashboard, documents, reports,
    notifications, interaction, monitoring, arrears
)
from datetime import datetime
from app.core.database import engine, Base
from app.config import settings
from fastapi.responses import FileResponse
import os
from app.tasks.scheduler import start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events
    """
    # Startup
    logger.info("Starting up Rental Management System...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background scheduler
    scheduler = start_scheduler()
    
    # Schedule DB backup (simulated every hour for demo)
    from app.tasks.backup import run_backup
    from app.tasks.reminders import send_rent_reminders
    scheduler.add_job(run_backup, 'interval', hours=1)
    scheduler.add_job(send_rent_reminders, 'interval', days=1)
    
    app.state.scheduler = scheduler
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()
    await engine.dispose()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Rental Management System for Landlords",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(properties.router, prefix=f"{settings.API_V1_STR}/properties", tags=["Properties"])
app.include_router(tenants.router, prefix=f"{settings.API_V1_STR}/tenants", tags=["Tenants"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["Payments"])
app.include_router(maintenance.router, prefix=f"{settings.API_V1_STR}/maintenance", tags=["Maintenance"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])
app.include_router(interaction.router, prefix=f"{settings.API_V1_STR}/interactions", tags=["Interactions"])
app.include_router(monitoring.router, prefix=f"{settings.API_V1_STR}/monitoring", tags=["Monitoring"])
app.include_router(arrears.router, prefix=f"{settings.API_V1_STR}/arrears", tags=["Arrears"])

# Admin Router (New)
from app.api.endpoints import admin
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Mount static files correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")