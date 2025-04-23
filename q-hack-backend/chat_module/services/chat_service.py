# chat_module/services/chat_service.py
from typing import Dict, Any, List, Optional
import json
import os
import logging

from .query_parser import QueryParser
from .llm_service import LLMService
from ..config import ChatConfig

class ChatService:
    """Main service to handle chat interactions about startups."""
    
    def __init__(self):
        self.config = ChatConfig
        self.query_parser = QueryParser()
        self.llm_service = LLMService()
        
        # Create log directory if it doesn't exist and logging is enabled
        if self.config.ENABLE_LOGGING:
            log_dir = os.path.dirname(self.config.LOG_PATH)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            # Configure logging
            logging.basicConfig(
                filename=self.config.LOG_PATH,
                level=logging.INFO,
                format='%(asctime)s - %(message)s'
            )
    
    async def process_query(
        self, 
        query: str, 
        company_data: Dict[str, Any],
        conversation_id: str,
        message_history: List[Dict[str, str]] = []
    ) -> Dict[str, Any]:
        """
        Process a user query about a startup.
        
        This implements our hybrid approach:
        1. Try to match query to specific data fields
        2. If direct match fails, use LLM for more complex reasoning
        
        Args:
            query: The user's question
            company_data: The structured company data
            conversation_id: Unique ID for the conversation
            message_history: Previous messages in the conversation
            
        Returns:
            Dict with response data
        """
        # Log the incoming query if logging is enabled
        if self.config.ENABLE_LOGGING:
            company_name = company_data.get("company_name", "Unknown Company")
            logging.info(f"Conversation ID: {conversation_id}")
            logging.info(f"Company: {company_name}")
            logging.info(f"Query: {query}")
        
        # Try to parse with simple rules first
        is_direct_match, matched_data, matched_fields = self.query_parser.parse_query(query, company_data)
        
        # If we got direct matches and data, format a response
        if is_direct_match and matched_data:
            response = await self._format_direct_match_response(query, matched_data, matched_fields)
            
            # Log the response if logging is enabled
            if self.config.ENABLE_LOGGING:
                logging.info(f"Response type: Direct match")
                logging.info(f"Fields: {matched_fields}")
                logging.info(f"Response: {response['answer']}")
                logging.info("-" * 50)
                
            return response
        
        # If we matched fields but didn't find data, note the specific missing data
        if is_direct_match and not matched_data:
            response = {
                "answer": f"I don't have information about {', '.join(matched_fields)} for this startup.",
                "source_fields": matched_fields,
                "confidence": 0.9
            }
            
            # Log the response if logging is enabled
            if self.config.ENABLE_LOGGING:
                logging.info(f"Response type: Missing data")
                logging.info(f"Fields: {matched_fields}")
                logging.info(f"Response: {response['answer']}")
                logging.info("-" * 50)
                
            return response
        
        # No direct match, use LLM for complex reasoning
        response = await self.llm_service.process_complex_query(
            query=query,
            company_data=company_data,
            conversation_history=message_history
        )
        
        # Log the LLM response if logging is enabled
        if self.config.ENABLE_LOGGING:
            logging.info(f"Response type: LLM")
            logging.info(f"Model: {response.get('model_used', 'unknown')}")
            logging.info(f"Response: {response['answer'][:100]}...")
            logging.info("-" * 50)
            
        return response
    
    async def _format_direct_match_response(
        self, 
        query: str, 
        matched_data: Dict[str, Any],
        matched_fields: List[str]
    ) -> Dict[str, Any]:
        """Format a response for direct field matches."""
        
        # Convert the matched data into a readable response
        response_parts = []
        
        for field, value in matched_data.items():
            # Handle different data types
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
                elif field == "traction.customer_validation.testimonials":
                    response_parts.append(f"Customer testimonials: {', '.join(value)}")
                else:
                    response_parts.append(f"{field.split('.')[-1]}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                # For nested dictionaries, include all key-value pairs
                nested_parts = []
                for k, v in value.items():
                    nested_parts.append(f"{k}: {v}")
                response_parts.append(f"{field.split('.')[-1]}: {', '.join(nested_parts)}")
            else:
                # Field name formatting
                field_name = field.split('.')[-1]
                field_name = field_name.replace('_', ' ').title()
                
                response_parts.append(f"{field_name}: {value}")
        
        # Join all parts into a cohesive response
        response = " ".join(response_parts)
        
        return {
            "answer": response,
            "source_fields": matched_fields,
            "confidence": 1.0  # Higher confidence for direct matches
        }