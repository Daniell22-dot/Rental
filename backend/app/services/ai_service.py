import httpx
from app.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"

    async def get_chat_response(self, prompt: str, system_content: str = "You are a helpful assistant for a Rental Management System."):
        if not self.api_key or self.api_key == "your_key_here":
            return {"error": "DeepSeek API key not configured"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_content},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
            except Exception as e:
                return {"error": str(e)}

ai_service = AIService()
