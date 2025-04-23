# email_module/services/contact_finder.py
import requests
import logging
from email_module.config import EmailConfig

class ContactFinder:
    def __init__(self):
        self.config = EmailConfig
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("contact_finder")
    
    async def find_email(self, company_name, domain=None):
        #in order to stop making an api call every time, needs to be deleted in prod
        return f"contact@{domain}"
        """Find company email using free APIs."""
        
        self.logger.info(f"Searching for email for {company_name} with domain {domain}")
        self.logger.info(f"Hunter API Key present: {bool(self.config.HUNTER_API_KEY)}")
        
        # Try Hunter.io's free tier if API key is available
        if domain and self.config.HUNTER_API_KEY:
            try:
                self.logger.info(f"Calling Hunter.io API for domain: {domain}")
                url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.config.HUNTER_API_KEY}"
                self.logger.info(f"URL: {url}")
                
                response = requests.get(url)
                self.logger.info(f"Hunter.io response status: {response.status_code}")
                
                data = response.json()
                self.logger.info(f"Hunter.io response data: {data}")
                
                if response.status_code == 200 and data.get("data", {}).get("emails"):
                    # Return the first generic email (like info@, contact@)
                    for email in data["data"]["emails"]:
                        if email["type"] in ["generic", "support"]:
                            self.logger.info(f"Found generic email: {email['value']}")
                            return email["value"]
                    
                    # If no generic email found, return the first one
                    first_email = data["data"]["emails"][0]["value"]
                    self.logger.info(f"No generic email found, using first: {first_email}")
                    return first_email
                else:
                    self.logger.info("No emails found in Hunter.io response")
            except Exception as e:
                self.logger.error(f"Error using Hunter API: {str(e)}")
        else:
            self.logger.info("Skipping Hunter.io API (no key or domain)")
        
        # Fallback: Generate common email formats based on domain
        if domain:
            common_formats = [
                f"contact@{domain}",
                f"info@{domain}",
                f"hello@{domain}",
                f"founders@{domain}"
            ]
            self.logger.info(f"Using fallback email: {common_formats[0]}")
            return common_formats[0]  # Return first format as fallback
        
        self.logger.warning("No domain provided, cannot determine email")
        return None