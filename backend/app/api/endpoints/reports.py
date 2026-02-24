from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.ai_service import ai_service
from app.api.endpoints.admin import get_system_stats

router = APIRouter()

@router.get("/ai-narrative")
async def get_ai_financial_narrative(db: AsyncSession = Depends(get_db)):
    # Get current stats
    stats = await get_system_stats()
    
    # Narrative Prompt
    prompt = f"""
    Analyze these property statistics for Baringo County rental management and provide a concise, 
    professional summary for the owner. 
    Focus on net profit and tax implications.
    Stats: {stats}
    """
    
    narrative = await ai_service.get_chat_response(prompt, "You are a financial analyst specializing in Kenyan real estate.")
    
    return {
        "stats": stats,
        "narrative": narrative
    }
