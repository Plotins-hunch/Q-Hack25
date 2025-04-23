#!/usr/bin/env python3
"""
Standalone test for the chat functionality.
Run this directly from any directory: python standalone_test.py
"""

import re
import json
from typing import Dict, Any, List, Tuple

# Simple implementation of query parser for testing
class SimpleQueryParser:
    """Simplified query parser for testing."""
    
    def __init__(self):
        # Define simplified query patterns for testing
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
            
            # Funding queries
            (r"\b(?:funding stage|investment stage)\b", ["funding.stage"]),
            (r"\b(?:funding amount|raised|investment amount|how much.*raised)\b", ["funding.amount"]),
            
            # Financial efficiency
            (r"\b(?:burn rate|cash burn|burning)\b", ["financial_efficiency.burn_rate"]),
        ]
    
    def parse_query(self, query: str, company_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Parse a user query to see if it matches any patterns."""
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


# Sample company data
sample_data = {
    "company_name": "TechInnovate",
    "team": {
        "founders": [
            {"name": "Jane Smith", "background": "Ex-Google AI researcher"},
            {"name": "Mike Johnson", "background": "Serial entrepreneur, 2 exits"}
        ],
        "team_strength": "Strong technical expertise in AI and machine learning",
        "network_strength": "Well-connected in Silicon Valley VC community"
    },
    "market": {
        "TAM": "$50B globally",
        "SAM": "$15B in North America and Europe",
        "SOM": "$2.5B in first 3 years",
        "growth_rate": "18% CAGR"
    },
    "product": {
        "stage": "MVP with 5 beta customers",
        "USP": "AI-driven predictive maintenance reducing downtime by 35%",
        "customer_acquisition": "Direct sales to enterprise, 3-month sales cycle"
    },
    "funding": {
        "stage": "Seed",
        "amount": "$2.1M"
    },
    "financial_efficiency": {
        "burn_rate": "$95K monthly"
    }
}

# Function to test a query
def test_query(query, parser, data):
    print(f"\nQuery: {query}")
    is_match, matched_data, fields = parser.parse_query(query, data)
    
    if is_match:
        print(f"✓ Match found!")
        print(f"Fields: {fields}")
        
        if matched_data:
            for field, value in matched_data.items():
                if isinstance(value, list):
                    if field == "team.founders":
                        founders = [f"{f.get('name')} ({f.get('background')})" for f in value]
                        print(f"Founders: {', '.join(founders)}")
                    else:
                        print(f"{field}: {value}")
                else:
                    print(f"{field}: {value}")
        else:
            print("! No data found for these fields")
    else:
        print("✗ No direct match found")
    
    print("-" * 50)

def main():
    print("=== STANDALONE CHAT QUERY PARSER TEST ===")
    print("This test runs completely independently without any imports.")
    
    # Create parser instance
    parser = SimpleQueryParser()
    
    # Test various queries
    test_queries = [
        "Who are the founders?",
        "What's the funding stage?",
        "How much funding have they raised?",
        "What's their burn rate?",
        "Tell me about their team strength",
        "What's their total addressable market?",
        "How do they acquire customers?",
        "Is this a good investment?",  # Should not match
    ]
    
    for query in test_queries:
        test_query(query, parser, sample_data)
    
    # Test with missing data
    print("\n=== TESTING WITH MISSING DATA ===")
    incomplete_data = json.loads(json.dumps(sample_data))
    del incomplete_data["funding"]["stage"]
    
    test_query("What's their funding stage?", parser, incomplete_data)
    
if __name__ == "__main__":
    main()