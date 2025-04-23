# chat_module/models/chat_models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    """Model for a chat request."""
    query: str
    company_data: Dict[str, Any]
    conversation_id: Optional[str] = None
    message_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    """Model for a chat response."""
    response_text: str
    conversation_id: str
    source_fields: Optional[List[str]] = None
    is_llm_response: bool = False