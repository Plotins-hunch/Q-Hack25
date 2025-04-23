# email_module/services/template_engine.py
from jinja2 import Environment, FileSystemLoader
import os

class EmailTemplateEngine:
    def __init__(self):
        # Get the path to the templates directory
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_email(self, startup_data, missing_fields):
        """Generate HTML email content requesting missing information."""
        template = self.env.get_template("data_request.html")
        
        # Extract company name from data
        company_name = startup_data.get("company_overview", {}).get("name", "Your Company")
        
        # Render template with data
        return template.render(
            company_name=company_name,
            missing_fields=missing_fields,
            # Add any other template variables needed
        )