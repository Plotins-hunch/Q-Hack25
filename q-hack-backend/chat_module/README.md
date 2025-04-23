# Startup Analyzer Chat Module

This module provides an AI-powered chat interface to query startup data. It uses a hybrid approach combining pattern matching for direct queries and LLM-powered analysis for complex questions.

## Features

- Direct field matching for common queries (funding, team, market size, etc.)
- LLM-based reasoning for complex analysis queries
- Conversation history tracking
- Suggested questions based on available data

## API Endpoints

### Query Endpoint

**POST** `/api/chat/query`

Request body:
```json
{
  "company_data": {
    // Full company JSON structure
  },
  "query": "Who are the founders?",
  "conversation_id": "optional-existing-conversation-id",
  "message_history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ]
}
```

Response:
```json
{
  "response_text": "The founders are Jane Smith (Ex-Google AI researcher) and Mike Johnson (Serial entrepreneur, 2 exits)",
  "conversation_id": "uuid",
  "source_fields": ["team.founders"],
  "confidence": 1.0,
  "timestamp": "2023-04-23T15:30:22.123456"
}
```

### Suggestions Endpoint

**GET** `/api/chat/suggestions/{company_id}`

Response:
```json
{
  "suggestions": [
    "What's the funding stage of this startup?",
    "Who are the founders?",
    "What is their burn rate?",
    // More suggestions
  ]
}
```

## How It Works

1. **Query Parsing**: First tries to match the query to specific JSON fields using regex patterns
2. **Direct Field Access**: If a match is found, returns the data directly from those fields
3. **LLM Processing**: For complex queries or those without direct field matches, uses GPT-4 to analyze the startup data
4. **Conversation Context**: Maintains conversation history for context-aware responses

## Requirements

- Python 3.8+
- FastAPI
- OpenAI API key (configured in .env file)

## Setup

1. Configure your environment variables in the .env file:
   ```
   # OpenAI API configuration
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4
   OPENAI_TEMPERATURE=0.3
   OPENAI_MAX_TOKENS=500
   
   # Feature flags
   ENABLE_CHAT_LOGGING=true
   ```

2. The module is automatically loaded when the FastAPI app starts
   
3. Check the .env.template file for all available configuration options

## Testing

Run the test script to verify functionality:
```
python test_chat.py
```

## Extending

- Add more query patterns in `query_parser.py`
- Enhance response formatting in `chat_service.py`
- Implement dynamic suggestion generation based on available data