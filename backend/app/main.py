# backend/app/main.py
from fastapi import FastAPI, HTTPException
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
from fastapi.responses import FileResponse, RedirectResponse
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
    scheduler.add_job(run_backup, 'interval', hours=24)
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
from app.api.endpoints import admin, users
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Redirect admin/landlord UI requests on port 8001 to separate ports


# Mount static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))

# Ensure frontend directory exists
if not os.path.exists(FRONTEND_DIR):
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    logger.warning(f"Created frontend directory at {FRONTEND_DIR}")

# Mount static files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/admin")
async def serve_admin_login():
    """Serve admin login page"""
    file_path = os.path.join(FRONTEND_DIR, "admin-login.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Admin login page not found")

@app.get("/landlord")
async def serve_landlord_login():
    """Serve landlord login page"""
    file_path = os.path.join(FRONTEND_DIR, "landlord-login.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Landlord login page not found")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend files"""
    file_path = os.path.join(FRONTEND_DIR, full_path)
    
    # If it's a file that exists, serve it
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For routes that don't match files, serve index.html (SPA support)
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)