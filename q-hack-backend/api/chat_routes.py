# backend/api/chat_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid

from chat_module.services.query_parser import QueryParser
from chat_module.services.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize services
query_parser = QueryParser()
llm_service = LLMService()

class StartupQuery(BaseModel):
    """Model for chat queries about a startup."""
    company_data: Dict[str, Any]
    query: str
    conversation_id: Optional[str] = None
    message_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    """Model for chat responses."""
    response_text: str
    conversation_id: str
    source_fields: Optional[List[str]] = None
    is_llm_response: bool = False

@router.post("/query", response_model=ChatResponse)
async def query_startup(request: StartupQuery):
    """Process a chat query about a startup."""
    
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Try direct matching first
    is_direct_match, matched_data, matched_fields = query_parser.parse_query(
        request.query, request.company_data
    )
    
    # If we got direct matches and data, format a response
    if is_direct_match and matched_data:
        # Format the response from matched data
        response_parts = []
        
        for field, value in matched_data.items():
            # Special handling for different data types
            if isinstance(value, list):
                if field == "team.founders":
                    founders_info = []
                    for founder in value:
                        if isinstance(founder, dict):
                            founder_desc = f"{founder.get('name', 'Unnamed')}"
                            if founder.get('background'):
                                founder_desc += f" ({founder.get('background')})"
                            founders_info.append(founder_desc)
                        else:
                            founders_info.append(str(founder))
                    response_parts.append(f"The founders are: {', '.join(founders_info)}")
                elif field == "funding.investors_on_board":
                    investors_info = []
                    for investor in value:
                        if isinstance(investor, dict):
                            investor_desc = f"{investor.get('name', 'Unnamed')}"
                            if investor.get('type'):
                                investor_desc += f" ({investor.get('type')})"
                            investors_info.append(investor_desc)
                        else:
                            investors_info.append(str(investor))
                    response_parts.append(f"The investors include: {', '.join(investors_info)}")
                else:
                    response_parts.append(f"{field.split('.')[-1]}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                nested_parts = []
                for k, v in value.items():
                    nested_parts.append(f"{k}: {v}")
                response_parts.append(f"{field.split('.')[-1]}: {', '.join(nested_parts)}")
            else:
                field_name = field.split('.')[-1]
                field_name = field_name.replace('_', ' ').title()
                response_parts.append(f"{field_name}: {value}")
        
        # Join all parts into a cohesive response
        response_text = " ".join(response_parts)
        
        return ChatResponse(
            response_text=response_text,
            conversation_id=conversation_id,
            source_fields=matched_fields,
            is_llm_response=False
        )
    
    # If we matched fields but didn't find data, note the specific missing data
    if is_direct_match and not matched_data:
        return ChatResponse(
            response_text=f"I don't have information about {', '.join(matched_fields)} for this startup.",
            conversation_id=conversation_id,
            source_fields=matched_fields,
            is_llm_response=False
        )
    
    # No direct match, use LLM for complex reasoning
    try:
        # Use LLM service (synchronous)
        llm_response = llm_service.process_complex_query(
            request.query,
            request.company_data,
            request.message_history
        )
        
        return ChatResponse(
            response_text=llm_response["answer"],
            conversation_id=conversation_id,
            is_llm_response=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/suggestions")
async def get_suggested_questions():
    """Get suggested questions for the chat."""
    return {
        "suggestions": [
            "Who are the founders?",
            "What's the funding stage?",
            "How much funding have they raised?", 
            "What's their burn rate?",
            "What's their market size?",
            "Is this startup a good investment?",
            "What are the main risks for this company?"
        ]
    }