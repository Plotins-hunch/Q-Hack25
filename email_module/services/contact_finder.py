# email_module/services/contact_finder.py
import requests
from email_module.config import EmailConfig

class ContactFinder:
    def __init__(self):
        self.config = EmailConfig
    
    async def find_email(self, company_name, domain=None):
        """Find company email using free APIs."""
        
        # Try Hunter.io's free tier if API key is available
        if domain and self.config.HUNTER_API_KEY:
            try:
                response = requests.get(
                    f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.config.HUNTER_API_KEY}"
                )
                data = response.json()
                
                if response.status_code == 200 and data.get("data", {}).get("emails"):
                    # Return the first generic email (like info@, contact@)
                    for email in data["data"]["emails"]:
                        if email["type"] in ["generic", "support"]:
                            return email["value"]
                    
                    # If no generic email found, return the first one
                    return data["data"]["emails"][0]["value"]
            except Exception as e:
                print(f"Error using Hunter API: {str(e)}")
        
        # Fallback: Generate common email formats based on domain
        if domain:
            common_formats = [
                f"contact@{domain}",
                f"info@{domain}",
                f"hello@{domain}",
                f"founders@{domain}"
            ]
            return common_formats[0]  # Return first format as fallback
            
        return None