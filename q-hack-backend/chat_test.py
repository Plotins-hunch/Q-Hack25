#!/usr/bin/env python3
"""
Simplified test script for the chat module.
Run this from the root directory with: python chat_test.py
"""

import json
import asyncio
import os
from dotenv import load_dotenv

# Import chat services directly
from chat_module.services.chat_service import ChatService
from chat_module.services.query_parser import QueryParser
from chat_module.services.llm_service import LLMService

# Load environment variables from .env file
load_dotenv()

# Verify API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not set in .env file. Tests requiring LLM will fail.")

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

async def test_direct_queries():
    """Test queries that should match directly to fields."""
    
    chat_service = ChatService()
    
    test_queries = [
        "Who are the founders?",
        "What's the funding stage?",
        "How much funding have they raised?",
        "What's their burn rate?",
        "Tell me about their team strength",
        "What's their total addressable market?",
        "How do they acquire customers?"
    ]
    
    print("===== DIRECT QUERY TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=sample_data,
            conversation_id="test-123",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print(f"Fields: {response.get('source_fields', [])}")
        print("-" * 50)

async def test_complex_queries():
    """Test queries that require LLM processing."""
    
    chat_service = ChatService()
    
    test_queries = [
        "Is this startup a good investment?",
        "What are the main risks for this company?",
        "Compare their CAC and LTV - is it sustainable?",
        "What's their competitive advantage?",
        "Do they have good unit economics?"
    ]
    
    print("===== COMPLEX QUERY TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=sample_data,
            conversation_id="test-456",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print(f"Model: {response.get('model_used', 'N/A')}")
        print("-" * 50)

async def test_missing_data_queries():
    """Test queries for data that doesn't exist."""
    
    # Create a copy with some data removed
    incomplete_data = json.loads(json.dumps(sample_data))
    del incomplete_data["funding"]["stage"]
    del incomplete_data["financial_efficiency"]["burn_rate"]
    
    chat_service = ChatService()
    
    test_queries = [
        "What's their funding stage?",
        "What's their burn rate?",
    ]
    
    print("===== MISSING DATA TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=incomplete_data,
            conversation_id="test-789",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print("-" * 50)

# This allows the script to be run directly
if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_direct_queries())
    try:
        # Only run these if the API key is set
        if os.getenv("OPENAI_API_KEY"):
            asyncio.run(test_complex_queries())
        else:
            print("\n===== SKIPPING COMPLEX QUERY TESTS (No API key) =====\n")
    except Exception as e:
        print(f"Error in complex queries: {str(e)}")
    
    asyncio.run(test_missing_data_queries())