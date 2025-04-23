# chat_module/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path="../.env")

class ChatConfig:
    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Model configuration
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
    # Feature flags - DISABLED for hackathon use
    ENABLE_LOGGING = False
    LOG_PATH = os.path.join(os.getcwd(), "chat_logs.log")
    
    @classmethod
    def is_api_key_set(cls):
        return bool(cls.OPENAI_API_KEY)