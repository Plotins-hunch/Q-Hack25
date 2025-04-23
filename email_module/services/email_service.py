# email_module/services/email_service.py
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os

from email_module.config import EmailConfig
from email_module.mocks.responses import generate_mock_response

class EmailService:
    def __init__(self):
        self.config = EmailConfig
        
        # Set up logging directory if needed
        if self.config.is_dev_mode() and self.config.LOG_EMAILS:
            log_dir = os.path.dirname(self.config.EMAIL_LOG_PATH)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            logging.basicConfig(
                filename=self.config.EMAIL_LOG_PATH,
                level=logging.INFO,
                format='%(asctime)s - %(message)s'
            )
    
    async def send_email(self, to_email, subject, html_content, startup_data, missing_fields):
        """Send email with toggle between real sending and development mode."""
        
        msg = MIMEMultipart()
        msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))
        
        # Dev mode: log email instead of sending
        if self.config.is_dev_mode():
            if self.config.LOG_EMAILS:
                logging.info(f"TO: {to_email}")
                logging.info(f"SUBJECT: {subject}")
                logging.info(f"CONTENT: {html_content}")
                logging.info("-" * 50)
            
            # Generate a mock response for demo purposes
            company_name = startup_data.get("company_overview", {}).get("name", "Your Company")
            mock_response = generate_mock_response(company_name, missing_fields)
            
            return {
                "status": "simulated",
                "message_id": f"dev-{datetime.now().timestamp()}",
                "mock_response": mock_response
            }
        
        # Production mode: actually send the email
        else:
            try:
                with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                    server.send_message(msg)
                    
                return {
                    "status": "sent",
                    "message_id": f"prod-{datetime.now().timestamp()}"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }