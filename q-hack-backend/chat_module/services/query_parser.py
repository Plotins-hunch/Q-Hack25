# chat_module/services/query_parser.py
import re
from typing import Dict, Any, List, Tuple, Optional

class QueryParser:
    """Service to parse user queries and map them to company data fields."""
    
    def __init__(self):
        # Define query patterns and their corresponding JSON paths
        self.query_patterns = [
            # Team queries
            (r"(?:who|what).*\b(?:founder|founders|founding team|co-founder)\b", ["team.founders"]),
            (r"(?:team|founding team) (background|experience|expertise)", ["team.team_strength"]),
            (r"(?:team|network) connections", ["team.network_strength"]),
            
            # Market queries
            (r"\b(?:TAM|total addressable market|market size)\b", ["market.TAM"]),
            (r"\b(?:SAM|serviceable available market)\b", ["market.SAM"]),
            (r"\b(?:SOM|serviceable obtainable market|target market)\b", ["market.SOM"]),
            (r"\b(?:market growth|growth rate)\b", ["market.growth_rate"]),
            
            # Product queries
            (r"\b(?:product stage|development stage|what stage)\b", ["product.stage"]),
            (r"\b(?:USP|unique selling proposition|competitive advantage|value proposition)\b", ["product.USP"]),
            (r"\b(?:customer acquisition|acquire customers|get customers)\b", ["product.customer_acquisition"]),
            
            # Traction queries
            (r"\b(?:MRR|monthly recurring revenue)\b", ["traction.revenue_growth.MRR"]),
            (r"\b(?:ARR|annual recurring revenue)\b", ["traction.revenue_growth.ARR"]),
            (r"\b(?:user growth|growing users|customer growth)\b", ["traction.user_growth"]),
            (r"\b(?:engagement|user engagement)\b", ["traction.engagement"]),
            (r"\b(?:testimonials|customer testimonials)\b", ["traction.customer_validation.testimonials"]),
            (r"\b(?:churn|churn rate)\b", ["traction.customer_validation.churn"]),
            (r"\b(?:NPS|net promoter score)\b", ["traction.customer_validation.NPS"]),
            
            # Funding queries
            (r"\b(?:funding stage|investment stage)\b", ["funding.stage"]),
            (r"\b(?:funding amount|raised|investment amount|how much.*raised)\b", ["funding.amount"]),
            (r"\b(?:cap table|capitalization)\b", ["funding.cap_table_strength"]),
            (r"\b(?:investors|investor list)\b", ["funding.investors_on_board"]),
            
            # Financial efficiency
            (r"\b(?:burn rate|cash burn|burning)\b", ["financial_efficiency.burn_rate"]),
            (r"\b(?:CAC|customer acquisition cost|LTV|lifetime value|CAC\/LTV)\b", ["financial_efficiency.CAC_vs_LTV"]),
            (r"\b(?:unit economics)\b", ["financial_efficiency.unit_economics"]),
            
            # Miscellaneous
            (r"\b(?:regulatory|regulations|compliance)\b", ["miscellaneous.regulatory_risk"]),
            (r"\b(?:geography|location|market location|geographic focus)\b", ["miscellaneous.geographic_focus"]),
            (r"\b(?:timing risk|fad risk|trend risk)\b", ["miscellaneous.timing_fad_risk"]),
            
            # Generic company queries
            (r"\b(?:company name|startup name|called)\b", ["company_name"]),
        ]
    
    def parse_query(self, query: str, company_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Parse a user query to see if it matches any of our patterns.
        
        Args:
            query: The user's question
            company_data: The structured company data
            
        Returns:
            Tuple containing:
            - Boolean indicating if a direct match was found
            - Dict with relevant data
            - List of JSON paths that were accessed
        """
        query = query.lower()
        matched_fields = []
        
        # Check each pattern for a match
        for pattern, field_paths in self.query_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                for path in field_paths:
                    matched_fields.append(path)
        
        # If no matches found, return False
        if not matched_fields:
            return False, {}, []
        
        # Extract the relevant data for matched fields
        response_data = {}
        for field_path in matched_fields:
            value = self._get_nested_value(company_data, field_path)
            if value:
                # Add to response data with the original path as key
                response_data[field_path] = value
        
        # If we found matches but no data, still return True but with empty data
        if not response_data:
            return True, {}, matched_fields
            
        return True, response_data, matched_fields
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Retrieve a value from a nested dictionary using dot notation path."""
        if not data:
            return None
            
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
                
        return current