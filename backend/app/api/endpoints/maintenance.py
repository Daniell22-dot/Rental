from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.maintenance import MaintenanceRequest
from app.services.ai_service import ai_service
import json

router = APIRouter()

@router.post("/")
async def create_maintenance_request(
    title: str, 
    description: str, 
    tenant_id: int, 
    property_id: int, 
    db: AsyncSession = Depends(get_db)
):
    # AI Triage Prompt
    triage_prompt = f"Categorize and prioritize this rental maintenance request:\nTitle: {title}\nDescription: {description}\n\nReturn ONLY a JSON object with 'priority' (low, medium, high, emergency) and 'category' (plumbing, electrical, structural, etc.)."
    system_msg = "You are a maintenance triage expert. Return only JSON."
    
    ai_result = await ai_service.get_chat_response(triage_prompt, system_msg)
    
    priority = "medium"
    category = "general"
    
    if isinstance(ai_result, str):
        try:
            # Clean possible markdown formatting
            cleaned_result = ai_result.strip().replace("```json", "").replace("```", "")
            data = json.loads(cleaned_result)
            priority = data.get("priority", "medium").lower()
            category = data.get("category", "general")
        except:
            pass
            
    new_request = MaintenanceRequest(
        title=title,
        description=description,
        tenant_id=tenant_id,
        property_id=property_id,
        status="pending",
        priority=priority
    )
    
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    
    return {
        "status": "success",
        "request_id": new_request.id,
        "ai_triage": {
            "priority": priority,
            "category": category
        }
    }
