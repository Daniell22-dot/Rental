from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_dashboard_stats():
    return {"message": "Dashboard stats endpoint"}
