# email_module/models/email_tracking.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class EmailRequest(BaseModel):
    """Model for tracking outgoing email requests."""
    id: Optional[str] = None  # Will be set to a UUID
    startup_id: str
    contact_email: str
    missing_fields: List[Dict[str, str]]
    sent_at: datetime = datetime.now()
    status: str = "sent"  # sent, delivered, responded, failed
    message_id: Optional[str] = None
    
    # For demo/dev purposes
    is_simulated: bool = False
    simulated_response: Optional[str] = None

class EmailResponse(BaseModel):
    """Model for tracking incoming email responses."""
    request_id: str  # Links to the original request
    received_at: datetime = datetime.now()
    content: str
    extracted_data: Dict[str, Any]