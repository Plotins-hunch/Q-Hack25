# email_module/services/missing_data.py
def detect_missing_fields(startup_data):
    """Analyze startup data and return missing fields with their descriptions."""
    
    missing_fields = []
    
    # Define critical fields with descriptions
    critical_fields = {
        "company_overview.name": "Company name",
        "company_overview.founded_year": "Year your company was founded",
        "business_model.revenue_model": "How your business generates revenue",
        "market.industry": "Your target industry",
        "market.market_size": "Estimated market size (in $)",
        "team": "Information about your founding team",
        "funding.funding_stage": "Current funding stage",
        "funding.amount": "Total funding raised to date",
        "financial_projections.burn_rate": "Monthly cash burn rate",
        "kpis.cac": "Customer Acquisition Cost",
        "kpis.ltv": "Customer Lifetime Value",
        "technology.stack": "Your technology stack"
    }
    
    # Check nested fields
    for field_path, description in critical_fields.items():
        parts = field_path.split('.')
        
        # Handle array field (team)
        if parts[0] == "team" and len(parts) == 1:
            if not startup_data.get("team") or len(startup_data["team"]) == 0:
                missing_fields.append({"field": field_path, "description": description})
            continue
                
        # Handle nested fields
        current = startup_data
        missing = False
        
        for part in parts:
            if part not in current or current[part] is None or current[part] == "":
                missing = True
                break
            current = current[part]
            
        if missing:
            missing_fields.append({"field": field_path, "description": description})
    
    return missing_fields