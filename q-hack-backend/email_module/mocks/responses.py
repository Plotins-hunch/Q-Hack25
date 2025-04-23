# email_module/mocks/responses.py
import random
import json
from datetime import datetime

def generate_mock_response(company_name, missing_fields):
    """Generate a simulated email response with missing data filled."""
    
    response_templates = [
        "Thanks for reaching out about {company}. Here's the information you requested:\n\n{data}",
        "Hello! I'm happy to provide the details you need about {company}:\n\n{data}",
        "Thanks for your interest in {company}. Please find the requested information below:\n\n{data}"
    ]
    
    # Generate realistic mock data for each missing field
    mock_data = {}
    field_responses = []
    
    for field in missing_fields:
        field_path = field["field"]
        description = field["description"]
        
        # Generate appropriate mock values based on field
        if "founded_year" in field_path:
            value = random.randint(2018, 2024)
        elif "funding.amount" in field_path:
            value = f"${random.choice([1.2, 2.5, 3.7, 5.0, 10.0])}M"
        elif "burn_rate" in field_path:
            value = f"${random.randint(50, 500)}K/month"
        elif "cac" in field_path:
            value = f"${random.randint(50, 500)}"
        elif "ltv" in field_path:
            value = f"${random.randint(500, 5000)}"
        elif "revenue_model" in field_path:
            models = ["SaaS subscription", "Freemium", "Transaction fees", "Licensing"]
            value = random.choice(models)
        elif "technology.stack" in field_path:
            tech_options = [
                "Python/Django, React, AWS", 
                "Node.js, Vue, Google Cloud",
                "Java Spring Boot, Angular, Azure"
            ]
            value = random.choice(tech_options)
        elif "market.industry" in field_path:
            industries = ["FinTech", "HealthTech", "EdTech", "CleanTech", "PropTech"]
            value = random.choice(industries)
        elif "market.market_size" in field_path:
            sizes = ["$1.2B", "$4.7B by 2028", "$850M with 12% CAGR"]
            value = random.choice(sizes)
        else:
            # Generic response for other fields
            value = f"Sample data for {description}"
        
        # Add to field responses
        field_responses.append(f"{description}: {value}")
    
    # Format the response
    data_section = "\n".join(field_responses)
    
    template = random.choice(response_templates)
    return template.format(company=company_name, data=data_section)