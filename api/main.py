import sys
import os

# This bridge file adds the backend directory to the path 
# so your existing imports inside backend/app work correctly on Vercel.

# Resolve the path to the backend directory
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

# Now we can safely import from backend.app.main
from app.main import handler as app

# Vercel looks for 'app' as the FastAPI instance
