# email_module/services/response_processor.py
import re
from typing import Dict, List, Any

class ResponseProcessor:
    def __init__(self):
        pass
        
    async def process_response(self, email_content: str, requested_fields: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract structured data from email responses."""
        extracted_data = {}
        
        # Simple rule-based extraction (for hackathon purposes)
        # In a production system, you'd use NLP/LLMs for better extraction
        for field in requested_fields:
            field_name = field["field"]
            description = field["description"].lower()
            
            # Create pattern variations to match field in email
            patterns = [
                rf"{re.escape(description)}:?\s*([^.\n]+)",
                rf"{field_name.split('.')[-1].replace('_', ' ')}:?\s*([^.\n]+)"
            ]
            
            # Try each pattern
            for pattern in patterns:
                matches = re.search(pattern, email_content.lower())
                if matches:
                    extracted_value = matches.group(1).strip()
                    
                    # Type conversion based on field
                    if "year" in field_name:
                        try:
                            extracted_value = int(re.search(r'\d{4}', extracted_value).group(0))
                        except:
                            pass
                    elif any(x in field_name for x in ["amount", "cac", "ltv", "burn_rate"]):
                        # Extract numeric value from currency
                        try:
                            extracted_value = re.search(r'[\d,.]+', extracted_value).group(0)
                        except:
                            pass
                    
                    # Store in the right nested structure
                    parts = field_name.split('.')
                    if len(parts) == 1:
                        extracted_data[parts[0]] = extracted_value
                    elif len(parts) == 2:
                        if parts[0] not in extracted_data:
                            extracted_data[parts[0]] = {}
                        extracted_data[parts[0]][parts[1]] = extracted_value
                    
                    break  # Stop after first match
        
        return extracted_data