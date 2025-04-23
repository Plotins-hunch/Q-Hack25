# backend/api/email_routes.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid

from email_module.services.missing_data import detect_missing_fields
from email_module.services.email_service import EmailService
from email_module.services.contact_finder import ContactFinder
from email_module.services.template_engine import EmailTemplateEngine
from email_module.services.response_processor import ResponseProcessor
from email_module.models.email_tracking import EmailRequest, EmailResponse

router = APIRouter(prefix="/api/email", tags=["email"])

# Initialize services
email_service = EmailService()
contact_finder = ContactFinder()
template_engine = EmailTemplateEngine()
response_processor = ResponseProcessor()

# In-memory storage for demo purposes
# In a real application, this would be a database
email_requests = {}
email_responses = {}

class StartupData(BaseModel):
    company_data: Dict[str, Any]
    contact_email: Optional[str] = None
    domain: Optional[str] = None

@router.post("/request-missing-data")
async def request_data(startup: StartupData, background_tasks: BackgroundTasks):
    """Send email requesting missing data from startup."""
    
    # 1. Find missing fields
    missing_fields = detect_missing_fields(startup.company_data)
    
    if not missing_fields:
        return {"status": "complete", "message": "No missing fields detected"}
    
    # 2. Find contact email if not provided
    contact_email = startup.contact_email
    if not contact_email and startup.domain:
        contact_email = await contact_finder.find_email(
            startup.company_data.get("company_overview", {}).get("name"),
            startup.domain
        )
    
    if not contact_email:
        raise HTTPException(status_code=400, detail="Could not determine contact email")
    
    # 3. Generate email content
    company_name = startup.company_data.get("company_overview", {}).get("name", "")
    email_subject = f"Data Request for {company_name}"
    email_html = template_engine.generate_email(
        startup.company_data,
        missing_fields
    )
    
    # 4. Send email (or log in dev mode)
    result = await email_service.send_email(
        contact_email,
        email_subject,
        email_html,
        startup.company_data,
        missing_fields
    )
    
    # 5. Create tracking record
    request_id = str(uuid.uuid4())
    email_request = EmailRequest(
        id=request_id,
        startup_id=company_name,  # Using name as ID for simplicity
        contact_email=contact_email,
        missing_fields=missing_fields,
        status=result["status"],
        message_id=result.get("message_id"),
        is_simulated="simulated" in result["status"],
        simulated_response=result.get("mock_response")
    )
    
    # Store in our "database"
    email_requests[request_id] = email_request
    
    # 6. If in dev mode with simulated response, process it
    if "mock_response" in result:
        # Process the mock response
        extracted_data = await response_processor.process_response(
            result["mock_response"], 
            missing_fields
        )
        
        # Create response record
        response_id = str(uuid.uuid4())
        email_response = EmailResponse(
            request_id=request_id,
            content=result["mock_response"],
            extracted_data=extracted_data
        )
        
        # Store in our "database"
        email_responses[response_id] = email_response
    
    # 7. Return result
    return {
        "status": result["status"],
        "message_id": result.get("message_id"),
        "request_id": request_id,
        "requested_fields": [field["field"] for field in missing_fields],
        "simulated_response": result.get("mock_response"),
        "extracted_data": extracted_data if "mock_response" in result else None
    }

@router.get("/requests")
async def get_email_requests():
    """Get all email requests (for demo purposes)."""
    return list(email_requests.values())

@router.get("/responses")
async def get_email_responses():
    """Get all email responses (for demo purposes)."""
    return list(email_responses.values())

@router.get("/request/{request_id}")
async def get_email_request(request_id: str):
    """Get specific email request by ID."""
    if request_id not in email_requests:
        raise HTTPException(status_code=404, detail="Email request not found")
    return email_requests[request_id]