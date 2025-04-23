#!/usr/bin/env python3
"""
Simple test script for the chat module.
Run this from inside the chat_module directory: python test_direct.py
"""

import json
import asyncio
import os
import logging
import sys

# Configure simple console logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

# Direct imports from the local directory structure
from services.query_parser import QueryParser
from services.chat_service import ChatService

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
    "traction": {
        "revenue_growth": {"MRR": "$25K", "ARR": "$300K"},
        "user_growth": "128% QoQ last two quarters",
        "engagement": "Daily active users at 78% of total users",
        "customer_validation": {
            "testimonials": [
                "Reduced our maintenance costs by 40% - CTO, ManufactureCo",
                "Game-changing for our operations - VP Ops, IndustrialTech"
            ],
            "churn": "2.3% monthly",
            "NPS": "72"
        }
    },
    "funding": {
        "stage": "Seed",
        "amount": "$2.1M",
        "cap_table_strength": "Clean, with SAFE notes",
        "investors_on_board": [
            {"name": "TechVentures", "type": "VC"},
            {"name": "AI Angels", "type": "Angel group"}
        ]
    },
    "financial_efficiency": {
        "burn_rate": "$95K monthly",
        "CAC_vs_LTV": "CAC: $12K, LTV: $85K",
        "unit_economics": "85% gross margin on SaaS offering"
    },
    "miscellaneous": {
        "regulatory_risk": "Low - no personal data handling",
        "geographic_focus": "North America initially, Europe in Year 2",
        "timing_fad_risk": "Low - solving persistent industrial problem"
    }
}

# Simple test function for direct query matching
def test_query(query, company_data):
    parser = QueryParser()
    is_match, data, fields = parser.parse_query(query, company_data)
    
    print(f"\nQuery: {query}")
    if is_match:
        print(f"Match found: {is_match}")
        print(f"Fields: {fields}")
        if data:
            print(f"Data: {data}")
        else:
            print("No data found for matched fields")
    else:
        print("No direct match found")
    print("-" * 50)

# Run a collection of tests
def run_tests():
    print("===== TESTING DIRECT QUERY PARSER =====")
    
    test_queries = [
        "Who are the founders?",
        "What's the funding stage?",
        "How much funding have they raised?",
        "What's their burn rate?",
        "Tell me about their team strength",
        "What's their total addressable market?",
        "How do they acquire customers?"
    ]
    
    for query in test_queries:
        test_query(query, sample_data)
        
    # Test with missing data
    print("\n===== TESTING WITH MISSING DATA =====")
    incomplete_data = json.loads(json.dumps(sample_data))
    del incomplete_data["funding"]["stage"]
    
    test_query("What's their funding stage?", incomplete_data)
    
if __name__ == "__main__":
    print("Starting simple query parser test...")
    run_tests()
    print("All tests completed!")