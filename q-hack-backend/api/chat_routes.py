from fastapi import APIRouter, Body, HTTPException, Depends
from typing import Dict, Any, List, Optional
import os
import uuid
import traceback
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Import services (with error handling to avoid circular imports)
try:
    from chat_module.services.chat_service import ChatService
    chat_service = ChatService()
except ImportError as e:
    print(f"Warning: Could not import ChatService: {e}")
    chat_service = None

class ChatRequest(BaseModel):
    query: str
    company_data: Dict[str, Any]
    conversation_id: Optional[str] = None
    message_history: Optional[List[Dict[str, str]]] = []

class SuggestionResponse(BaseModel):
    suggestions: List[str]

@router.post("/query")
async def query_chat(request: ChatRequest = Body(...)):
    """
    Process a chat query about startup data.

    The request should include:
    - The query text
    - The complete company data
    - Optional conversation ID and message history
    """
    if not chat_service:
        raise HTTPException(status_code=500, detail="Chat service not available")

    try:
        # Ensure we have valid company data
        if not request.company_data:
            return {
                "response_text": "I don't have any company data to analyze. Please provide company information.",
                "conversation_id": request.conversation_id or str(uuid.uuid4()),
                "error": "missing_data"
            }

        # Log request for debugging
        print(f"Processing chat query: {request.query}")
        print(f"Company data keys: {list(request.company_data.keys())}")

        # Process the query
        response = await chat_service.process_query(
            query=request.query,
            company_data=request.company_data,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            message_history=request.message_history or []
        )

        return {
            "response_text": response.get("answer", "I couldn't process that query."),
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "source_fields": response.get("source_fields", []),
            "is_llm_response": "model_used" in response
        }
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in chat query: {error_details}")

        return {
            "response_text": f"I encountered an error processing your request: {str(e)}",
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "error": "processing_error",
            "error_details": str(e)
        }

@router.get("/suggestions")
async def get_suggestions():
    """Get suggested questions to ask about a startup."""
    # These are static for now, but could be dynamically generated based on company data
    suggestions = [
        "What's the funding stage of this startup?",
        "Who are the founders?",
        "What is their burn rate?",
        "What is their total addressable market?",
        "How do they acquire customers?",
        "What are the main risks for this company?",
        "What's their business model?",
        "How is their team composition?"
    ]

    return SuggestionResponse(suggestions=suggestions)
