import httpx
import base64
from app.config import settings

async def ask_gpt5(text: str) -> str:
    """OpenAI Responses API 呼び出し"""
    if not settings.OPENAI_API_KEY:
        return "（OPENAI_API_KEY が未設定です）"
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}", 
        "Content-Type": "application/json"
    }
    body = {
        "model": settings.OPENAI_MODEL,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}]
    }
    if settings.OPENAI_MODEL.startswith("gpt-5"):
        body["reasoning"] = {"effort": "low"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        return data.get("output_text") or data["output"][0]["content"][0]["text"]

async def vision_extract_meal_bytes(data: bytes, mime: str | None) -> str:
    """画像バイナリを base64 で直接 OpenAI に渡して食事内容を短く要約"""
    if not settings.OPENAI_API_KEY:
        return "（OPENAI_API_KEY が未設定です）"
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}", 
        "Content-Type": "application/json"
    }
    instruction = (
        "この食事写真を短い日本語テキストで説明してください。"
        "料理名・主な食材・推定量を簡潔に。可能なら大まかなカロリーも一言で。"
    )
    b64 = base64.b64encode(data).decode("utf-8")
    body = {
        "model": settings.OPENAI_MODEL,
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text": instruction},
                {"type": "input_image", "image_data": {"data": b64, "mime_type": (mime or "image/jpeg")}},
            ],
        }]
    }
    if settings.OPENAI_MODEL.startswith("gpt-5"):
        body["reasoning"] = {"effort": "low"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
        r.raise_for_status()
        j = r.json()
        return j.get("output_text") or j["output"][0]["content"][0]["text"]
