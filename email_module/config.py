# email_module/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailConfig:
    # Mode configuration
    MODE = os.getenv("EMAIL_MODE", "development")  # Options: "development", "production"
    
    # Email service configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    FROM_EMAIL = os.getenv("FROM_EMAIL", "")
    FROM_NAME = os.getenv("FROM_NAME", "Startup Analyzer")
    
    # Development mode settings
    LOG_EMAILS = True
    EMAIL_LOG_PATH = "email_module/logs/sent_emails.log"
    
    # Contact finder API keys
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
    
    @classmethod
    def is_dev_mode(cls):
        return cls.MODE.lower() == "development"