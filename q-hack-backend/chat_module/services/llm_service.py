# chat_module/services/llm_service.py
import json
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

class LLMService:
    """Service to interface with GPT API for complex queries."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    def process_complex_query(
        self, 
        query: str, 
        company_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a complex query using GPT."""
        
        # Convert company_data to a formatted string
        company_data_str = json.dumps(company_data, indent=2)
        
        # Prepare conversation history if provided
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add system prompt
        messages = [
            {
                "role": "system", 
                "content": f"""You are an AI assistant specialized in startup analysis. 
                You will be given structured data about a startup and asked questions about it.
                Provide concise, accurate answers based ONLY on the data provided.
                If the data doesn't contain information to answer the question, say so clearly.
                Don't make up information that's not in the data.
                
                Here is the startup data:
                {company_data_str}
                """
            }
        ] + messages
        
        # Add the current user query
        messages.append({"role": "user", "content": query})
        
        try:
            # Call the OpenAI API using the new format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract the response
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "model_used": self.model
            }
            
        except Exception as e:
            # Handle API errors gracefully
            error_msg = f"Error communicating with LLM service: {str(e)}"
            return {
                "answer": f"I'm sorry, I couldn't process your question. {error_msg}",
                "error": str(e)
            }